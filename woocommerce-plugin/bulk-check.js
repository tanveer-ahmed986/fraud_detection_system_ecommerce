jQuery(document).ready(function($) {
    var csvData = [];
    var results = [];

    // Download template
    $('#download-template').on('click', function(e) {
        e.preventDefault();
        var csv = 'merchant_id,amount,currency,payment_method,user_id_hash,ip_hash,email_domain,is_new_user,device_type,billing_shipping_match,hour_of_day,day_of_week,items_count\n';
        csv += 'MERCH001,99.99,USD,credit_card,user123,192.168.1.1,gmail.com,false,desktop,true,14,2,2\n';
        csv += 'MERCH001,5000.00,USD,credit_card,user456,192.168.1.2,tempmail.com,true,mobile,false,3,1,1\n';
        csv += 'MERCH001,149.50,USD,paypal,user789,192.168.1.3,yahoo.com,false,desktop,true,10,3,1';

        var blob = new Blob([csv], { type: 'text/csv' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = 'fraud-check-template.csv';
        a.click();
    });

    // Handle CSV upload
    $('#csv-upload-form').on('submit', function(e) {
        e.preventDefault();

        var fileInput = $('#csv_file')[0];
        if (!fileInput.files.length) {
            alert('Please select a CSV file');
            return;
        }

        var file = fileInput.files[0];
        var reader = new FileReader();

        reader.onload = function(e) {
            var text = e.target.result;
            var debugHtml = '<strong>Debug Info:</strong><br>';
            debugHtml += 'File size: ' + text.length + ' bytes<br>';
            debugHtml += 'First 200 chars: ' + text.substring(0, 200).replace(/</g, '&lt;').replace(/>/g, '&gt;') + '<br>';

            $('#debug-info').html(debugHtml).show();

            csvData = parseCSV(text);

            $('#debug-info').append('Rows parsed: ' + csvData.length + '<br>');

            if (csvData.length === 0) {
                $('#debug-info').append('<span style="color: red;">ERROR: No data rows found!</span>');
                alert('CSV file is empty or invalid. Check the debug info above.');
                return;
            }

            $('#debug-info').append('<span style="color: green;">SUCCESS: Ready to process!</span><br>');
            console.log('CSV parsed successfully:', csvData.length, 'transactions');

            $('#upload-status').hide();
            $('#processing-status').show();
            $('#results-container').hide();

            setTimeout(function() {
                processBatch(0);
            }, 1000);
        };

        reader.onerror = function(e) {
            $('#debug-info').html('<span style="color: red;">Error reading file!</span>').show();
            alert('Error reading file: ' + e.target.error);
        };

        reader.readAsText(file);
    });

    function parseCSV(text) {
        text = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
        var lines = text.split('\n').filter(function(line) { return line.trim(); });

        if (lines.length === 0) {
            console.error('CSV has no lines');
            return [];
        }

        var headers = lines[0].split(',').map(function(h) { return h.trim(); });
        console.log('CSV Headers:', headers);

        if (headers.length === 0 || !headers[0]) {
            console.error('CSV has no headers');
            return [];
        }

        var data = [];
        for (var i = 1; i < lines.length; i++) {
            var values = lines[i].split(',');
            var row = {};
            for (var j = 0; j < headers.length; j++) {
                row[headers[j]] = values[j] ? values[j].trim() : '';
            }
            data.push(row);
        }

        console.log('Parsed ' + data.length + ' rows');
        return data;
    }

    function processBatch(startIndex) {
        var batchSize = 10;
        var batch = csvData.slice(startIndex, startIndex + batchSize);

        if (batch.length === 0) {
            showResults();
            return;
        }

        $.ajax({
            url: ajaxurl,
            type: 'POST',
            data: {
                action: 'tfshield_process_csv_batch',
                batch: JSON.stringify(batch),
                nonce: tfshieldBulkData.nonce
            },
            success: function(response) {
                if (response.success) {
                    results = results.concat(response.data.results);

                    var processed = startIndex + batch.length;
                    var total = csvData.length;
                    var percent = Math.round((processed / total) * 100);

                    $('#progress-bar').css('width', percent + '%').text(percent + '%');
                    $('#progress-text').html('Processed ' + processed + ' of ' + total + ' transactions...<br><em>⏱️ Please wait, this process may take a few minutes.</em>');

                    setTimeout(function() {
                        processBatch(startIndex + batchSize);
                    }, 500);
                } else {
                    alert('Error processing batch: ' + (response.data ? response.data.message : 'Unknown error'));
                }
            },
            error: function(xhr, status, error) {
                console.error('AJAX Error:', status, error);
                console.error('Response:', xhr.responseText);
                alert('Error connecting to server: ' + error);
            }
        });
    }

    function showResults() {
        $('#processing-status').hide();
        $('#results-container').show();

        var fraudCount = results.filter(function(r) { return r.label === 'HIGH RISK'; }).length;
        var legitCount = results.filter(function(r) { return r.label === 'LOW RISK'; }).length;
        var fraudAmount = results.filter(function(r) { return r.label === 'HIGH RISK'; })
            .reduce(function(sum, r) { return sum + parseFloat(r.amount || 0); }, 0);

        var summaryHtml = '';
        summaryHtml += '<div style="background: #f0f0f0; padding: 15px; border-radius: 4px;">';
        summaryHtml += '<div style="font-size: 24px; font-weight: bold;">' + results.length + '</div>';
        summaryHtml += '<div>Total Checked</div></div>';

        summaryHtml += '<div style="background: #fef2f2; padding: 15px; border-radius: 4px; border: 2px solid #dc3232;">';
        summaryHtml += '<div style="font-size: 24px; font-weight: bold; color: #dc3232;">' + fraudCount + '</div>';
        summaryHtml += '<div>🚨 High Risk</div></div>';

        summaryHtml += '<div style="background: #f0fdf4; padding: 15px; border-radius: 4px; border: 2px solid #46b450;">';
        summaryHtml += '<div style="font-size: 24px; font-weight: bold; color: #46b450;">' + legitCount + '</div>';
        summaryHtml += '<div>✅ Low Risk</div></div>';

        summaryHtml += '<div style="background: #fff7ed; padding: 15px; border-radius: 4px; border: 2px solid #f97316;">';
        summaryHtml += '<div style="font-size: 20px; font-weight: bold;">PKR ' + fraudAmount.toFixed(2) + '</div>';
        summaryHtml += '<div>💰 High Risk Amount Caught</div></div>';

        $('#results-summary').html(summaryHtml);

        var tableHTML = '<table class="wp-list-table widefat fixed striped"><thead><tr>';
        tableHTML += '<th>Order ID</th><th>Amount</th><th>Result</th><th>Confidence</th><th>Top Factor</th></tr></thead><tbody>';

        results.forEach(function(r) {
            var statusIcon = r.label === 'HIGH RISK' ? '🚨' : '✅';
            var statusColor = r.label === 'HIGH RISK' ? '#dc3232' : '#46b450';
            var confidence = (r.confidence * 100).toFixed(2) + '%';
            var topFactor = r.top_features && r.top_features[0] ? r.top_features[0].feature : 'N/A';

            tableHTML += '<tr>';
            tableHTML += '<td>' + r.order_id + '</td>';
            tableHTML += '<td>PKR ' + parseFloat(r.amount).toFixed(2) + '</td>';
            tableHTML += '<td style="color: ' + statusColor + '; font-weight: bold;">' + statusIcon + ' ' + r.label + '</td>';
            tableHTML += '<td>' + confidence + '</td>';
            tableHTML += '<td><code>' + topFactor + '</code></td>';
            tableHTML += '</tr>';
        });

        tableHTML += '</tbody></table>';
        $('#results-table-container').html(tableHTML);
    }

    // Download results
    $('#download-results').on('click', function() {
        downloadCSV(results, 'fraud-check-results.csv');
    });

    $('#download-fraud-only').on('click', function() {
        var fraudOnly = results.filter(function(r) { return r.label === 'HIGH RISK'; });
        downloadCSV(fraudOnly, 'high-risk-only.csv');
    });

    function downloadCSV(data, filename) {
        var csv = 'order_id,amount,label,confidence,top_factor_1,top_factor_2,top_factor_3\n';
        data.forEach(function(r) {
            var tf1 = r.top_features && r.top_features[0] ? r.top_features[0].feature : '';
            var tf2 = r.top_features && r.top_features[1] ? r.top_features[1].feature : '';
            var tf3 = r.top_features && r.top_features[2] ? r.top_features[2].feature : '';
            csv += r.order_id + ',' + r.amount + ',' + r.label + ',' + r.confidence + ',' + tf1 + ',' + tf2 + ',' + tf3 + '\n';
        });

        var blob = new Blob([csv], { type: 'text/csv' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
    }
});
