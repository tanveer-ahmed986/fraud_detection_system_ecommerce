<?php
/**
 * Plugin Name: AI Fraud Detection for WooCommerce
 * Plugin URI: https://github.com/tanveer-ahmed986/fraud_detection_system_ecommerce
 * Description: AI fraud detection with manual check, CSV bulk upload, and progress indicators
 * Version: 2.2.1
 * Author: Tanveer Ahmed
 * License: MIT
 * Requires at least: 5.8
 * Requires PHP: 7.4
 * WC requires at least: 8.0
 * WC tested up to: 10.6
 */

if (!defined('ABSPATH')) {
    exit;
}

if (!in_array('woocommerce/woocommerce.php', apply_filters('active_plugins', get_option('active_plugins')))) {
    return;
}

class WC_AI_Fraud_Detection_Manual {

    private static $instance = null;

    public static function get_instance() {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    private function __construct() {
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_action('admin_init', array($this, 'register_settings'));
        add_action('add_meta_boxes', array($this, 'add_fraud_meta_box'));
        add_action('admin_post_check_fraud', array($this, 'handle_manual_check'));
        add_action('wp_ajax_check_fraud_ajax', array($this, 'handle_ajax_check'));
        add_action('wp_ajax_process_csv_batch', array($this, 'handle_csv_batch'));
        add_action('admin_notices', array($this, 'show_admin_notices'));
        add_action('admin_enqueue_scripts', array($this, 'enqueue_scripts'));

        // AUTOMATIC FRAUD DETECTION on new orders (multiple hooks for reliability)
        if (class_exists('WooCommerce')) {
            add_action('woocommerce_new_order', array($this, 'auto_check_fraud'), 20, 1);
            add_action('woocommerce_payment_complete', array($this, 'auto_check_fraud'), 10, 1);
            add_action('woocommerce_order_status_processing', array($this, 'auto_check_fraud'), 10, 1);
        }
    }

    public function add_admin_menu() {
        add_submenu_page(
            'woocommerce',
            'AI Fraud Detection',
            'Fraud Detection',
            'manage_woocommerce',
            'wc-fraud-detection',
            array($this, 'render_settings_page')
        );

        // Add CSV Upload page
        add_submenu_page(
            'woocommerce',
            'Bulk Fraud Check (CSV)',
            'Bulk Check (CSV)',
            'manage_woocommerce',
            'wc-fraud-bulk-check',
            array($this, 'render_bulk_check_page')
        );
    }

    public function register_settings() {
        register_setting('wc_fraud_detection', 'wc_fraud_api_endpoint', array(
            'sanitize_callback' => 'esc_url_raw'
        ));
        register_setting('wc_fraud_detection', 'wc_fraud_api_key', array(
            'sanitize_callback' => 'sanitize_text_field'
        ));
        register_setting('wc_fraud_detection', 'wc_fraud_threshold', array(
            'sanitize_callback' => array($this, 'sanitize_threshold')
        ));
        register_setting('wc_fraud_detection', 'wc_fraud_auto_check', array(
            'sanitize_callback' => array($this, 'sanitize_checkbox')
        ));
        register_setting('wc_fraud_detection', 'wc_fraud_auto_hold', array(
            'sanitize_callback' => array($this, 'sanitize_checkbox')
        ));
        register_setting('wc_fraud_detection', 'wc_fraud_email_alerts', array(
            'sanitize_callback' => array($this, 'sanitize_checkbox')
        ));
    }

    public function sanitize_threshold($value) {
        $value = floatval($value);
        if ($value < 0) {
            $value = 0;
        } elseif ($value > 1) {
            $value = 1;
        }
        return $value;
    }

    public function sanitize_checkbox($value) {
        return $value === '1' ? '1' : '0';
    }

    public function render_bulk_check_page() {
        ?>
        <div class="wrap">
            <h1>📊 Bulk Fraud Check (CSV Upload)</h1>
            <p>Upload a CSV file to check multiple transactions for fraud. The system will analyze each transaction and provide results.</p>

            <div class="card" style="max-width: 800px; margin-top: 20px;">
                <h2>📁 Upload CSV File</h2>

                <div style="background: #f0f6fc; border: 1px solid #0969da; border-radius: 6px; padding: 15px; margin: 15px 0;">
                    <h3 style="margin-top: 0;">📋 CSV Format Requirements:</h3>
                    <p><strong>Required columns:</strong></p>
                    <code style="display: block; background: white; padding: 10px; margin: 10px 0;">
                        order_id,amount,payment_method,customer_email,is_new_customer,billing_city,items_count
                    </code>
                    <p><strong>Example row:</strong></p>
                    <code style="display: block; background: white; padding: 10px; margin: 10px 0;">
                        12345,99.99,credit_card,customer@example.com,yes,New York,2
                    </code>
                    <p style="margin-bottom: 0;">
                        <a href="#" id="download-template" class="button button-secondary">⬇️ Download CSV Template</a>
                    </p>
                </div>

                <form id="csv-upload-form" enctype="multipart/form-data" style="margin: 20px 0;">
                    <table class="form-table">
                        <tr>
                            <th><label for="csv_file">CSV File</label></th>
                            <td>
                                <input type="file" id="csv_file" name="csv_file" accept=".csv" required>
                                <p class="description">Select a CSV file to upload (max 10MB, 1000 rows)</p>
                            </td>
                        </tr>
                    </table>
                    <button type="submit" class="button button-primary button-large">
                        🚀 Start Fraud Check
                    </button>
                </form>

                <div id="upload-status" style="display: none; margin-top: 20px;"></div>
                <div id="debug-info" style="display: none; margin-top: 20px; background: #f0f0f0; padding: 15px; border-radius: 4px; font-family: monospace; font-size: 12px;"></div>
                <div id="processing-status" style="display: none; margin-top: 20px;">
                    <h3>⏳ Processing Transactions...</h3>
                    <div style="background: #f0f0f0; height: 30px; border-radius: 4px; overflow: hidden;">
                        <div id="progress-bar" style="background: linear-gradient(90deg, #0073aa, #00a0d2); height: 100%; width: 0%; transition: width 0.3s; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                            0%
                        </div>
                    </div>
                    <p id="progress-text" style="margin-top: 10px;">Processing... This may take a few minutes depending on file size.</p>
                </div>

                <div id="results-container" style="display: none; margin-top: 30px;">
                    <h2>✅ Results</h2>
                    <div style="margin-bottom: 15px;">
                        <button id="download-results" class="button button-secondary">⬇️ Download Results (CSV)</button>
                        <button id="download-fraud-only" class="button button-secondary">⚠️ Download Fraud Only</button>
                    </div>
                    <div id="results-summary" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px;"></div>
                    <div id="results-table-container" style="overflow-x: auto;"></div>
                </div>
            </div>
        </div>

        <script>
        jQuery(document).ready(function($) {
            var csvData = [];
            var results = [];

            // Download template
            $('#download-template').on('click', function(e) {
                e.preventDefault();
                var csv = 'order_id,amount,payment_method,customer_email,is_new_customer,billing_city,items_count\\n';
                csv += '12345,99.99,credit_card,customer@example.com,yes,New York,2\\n';
                csv += '12346,149.50,paypal,john@test.com,no,Los Angeles,1\\n';
                csv += '12347,250.00,credit_card,jane@example.com,yes,Chicago,5';

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
                // Handle different line endings (Windows: \r\n, Unix: \n, Mac: \r)
                text = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
                var lines = text.split('\n').filter(line => line.trim());

                if (lines.length === 0) {
                    console.error('CSV has no lines');
                    return [];
                }

                var headers = lines[0].split(',').map(h => h.trim());
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
                        action: 'process_csv_batch',
                        batch: JSON.stringify(batch),
                        nonce: '<?php echo wp_create_nonce('csv_batch'); ?>'
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
                            alert('Error processing batch: ' + response.data.message);
                        }
                    },
                    error: function() {
                        alert('Error connecting to server');
                    }
                });
            }

            function showResults() {
                $('#processing-status').hide();
                $('#results-container').show();

                var fraudCount = results.filter(r => r.label === 'fraud').length;
                var legitCount = results.filter(r => r.label === 'legitimate').length;
                var totalAmount = results.reduce((sum, r) => sum + parseFloat(r.amount || 0), 0);
                var fraudAmount = results.filter(r => r.label === 'fraud').reduce((sum, r) => sum + parseFloat(r.amount || 0), 0);

                $('#results-summary').html(`
                    <div style="background: #f0f0f0; padding: 15px; border-radius: 4px;">
                        <div style="font-size: 24px; font-weight: bold;">${results.length}</div>
                        <div>Total Checked</div>
                    </div>
                    <div style="background: #fef2f2; padding: 15px; border-radius: 4px; border: 2px solid #dc3232;">
                        <div style="font-size: 24px; font-weight: bold; color: #dc3232;">${fraudCount}</div>
                        <div>🚨 Fraud Detected</div>
                    </div>
                    <div style="background: #f0fdf4; padding: 15px; border-radius: 4px; border: 2px solid #46b450;">
                        <div style="font-size: 24px; font-weight: bold; color: #46b450;">${legitCount}</div>
                        <div>✅ Legitimate</div>
                    </div>
                    <div style="background: #fff7ed; padding: 15px; border-radius: 4px; border: 2px solid #f97316;">
                        <div style="font-size: 20px; font-weight: bold;">PKR ${fraudAmount.toFixed(2)}</div>
                        <div>💰 Fraud Amount Caught</div>
                    </div>
                `);

                var tableHTML = '<table class="wp-list-table widefat fixed striped"><thead><tr>';
                tableHTML += '<th>Order ID</th><th>Amount</th><th>Result</th><th>Confidence</th><th>Top Factor</th></tr></thead><tbody>';

                results.forEach(function(r) {
                    var statusIcon = r.label === 'fraud' ? '🚨' : '✅';
                    var statusColor = r.label === 'fraud' ? '#dc3232' : '#46b450';
                    var confidence = (r.confidence * 100).toFixed(2) + '%';
                    var topFactor = r.top_features && r.top_features[0] ? r.top_features[0].feature : 'N/A';

                    tableHTML += '<tr>';
                    tableHTML += '<td>' + r.order_id + '</td>';
                    tableHTML += '<td>PKR ' + parseFloat(r.amount).toFixed(2) + '</td>';
                    tableHTML += '<td style="color: ' + statusColor + '; font-weight: bold;">' + statusIcon + ' ' + r.label.toUpperCase() + '</td>';
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
                var fraudOnly = results.filter(r => r.label === 'fraud');
                downloadCSV(fraudOnly, 'fraud-detected-only.csv');
            });

            function downloadCSV(data, filename) {
                var csv = 'order_id,amount,label,confidence,top_factor_1,top_factor_2,top_factor_3\\n';
                data.forEach(function(r) {
                    var tf1 = r.top_features && r.top_features[0] ? r.top_features[0].feature : '';
                    var tf2 = r.top_features && r.top_features[1] ? r.top_features[1].feature : '';
                    var tf3 = r.top_features && r.top_features[2] ? r.top_features[2].feature : '';
                    csv += r.order_id + ',' + r.amount + ',' + r.label + ',' + r.confidence + ',' + tf1 + ',' + tf2 + ',' + tf3 + '\\n';
                });

                var blob = new Blob([csv], { type: 'text/csv' });
                var url = URL.createObjectURL(blob);
                var a = document.createElement('a');
                a.href = url;
                a.download = filename;
                a.click();
            }
        });
        </script>
        <?php
    }

    public function show_admin_notices() {
        $message = get_transient('wc_fraud_check_message');
        if ($message) {
            delete_transient('wc_fraud_check_message');
            if ($message === 'success') {
                echo '<div class="notice notice-success is-dismissible"><p><strong>✅ Fraud check completed successfully!</strong></p></div>';
            } else {
                echo '<div class="notice notice-error is-dismissible"><p><strong>❌ Fraud check failed. Check error logs.</strong></p></div>';
            }
        }
    }

    public function enqueue_scripts($hook) {
        if (strpos($hook, 'wc-orders') !== false || get_post_type() === 'shop_order') {
            wp_enqueue_script('wc-fraud-detection', plugin_dir_url(__FILE__) . 'fraud-detection.js', array('jquery'), '2.0.0', true);
            wp_localize_script('wc-fraud-detection', 'wcFraudDetection', array(
                'ajaxurl' => admin_url('admin-ajax.php'),
                'nonce' => wp_create_nonce('fraud_check_ajax')
            ));
        }
    }

    public function handle_ajax_check() {
        // Get order
        $order_id = isset($_POST['order_id']) ? intval($_POST['order_id']) : 0;
        if (!$order_id) {
            wp_send_json_error(array('message' => 'Invalid order ID'));
            return;
        }

        $order = wc_get_order($order_id);
        if (!$order) {
            wp_send_json_error(array('message' => 'Order not found'));
            return;
        }

        // Add initiation note
        $order->add_order_note('🔄 Starting fraud check...', false, true);

        // Get settings
        $api_endpoint = get_option('wc_fraud_api_endpoint', 'http://localhost:8000');

        // Prepare simple transaction data
        $transaction_data = array(
            'merchant_id' => get_bloginfo('name'),
            'amount' => floatval($order->get_total()),
            'payment_method' => $order->get_payment_method() ?: 'unknown',
            'user_id_hash' => 'test_user',
            'ip_hash' => 'test_ip',
            'email_domain' => 'test.com',
            'is_new_user' => true,
            'device_type' => 'unknown',
            'billing_shipping_match' => true,
            'hour_of_day' => 12,
            'day_of_week' => 1,
            'items_count' => $order->get_item_count()
        );

        // Call API
        $url = rtrim($api_endpoint, '/') . '/api/v1/predict';

        $response = wp_remote_post($url, array(
            'headers' => array('Content-Type' => 'application/json'),
            'body' => json_encode($transaction_data),
            'timeout' => 10,
            'sslverify' => false
        ));

        if (is_wp_error($response)) {
            $order->add_order_note('❌ API Error: ' . $response->get_error_message(), false, true);
            wp_send_json_error(array('message' => 'API connection failed'));
            return;
        }

        $body = wp_remote_retrieve_body($response);
        $fraud_result = json_decode($body, true);

        if ($fraud_result && isset($fraud_result['label'])) {
            // Save results
            $order->update_meta_data('_fraud_detection_result', $fraud_result);
            $order->update_meta_data('_fraud_detection_checked', current_time('mysql'));
            $order->save();

            // Add success note
            $is_fraud = ($fraud_result['label'] === 'fraud');
            $confidence = isset($fraud_result['confidence']) ? ($fraud_result['confidence'] * 100) : 0;

            $order->add_order_note(
                sprintf(
                    '🛡️ %s (Confidence: %.2f%%)',
                    $is_fraud ? '🚨 FRAUD' : '✅ Legitimate',
                    $confidence
                ),
                false,
                true
            );

            wp_send_json_success(array('message' => 'Success!'));
        } else {
            $order->add_order_note('❌ Invalid API response', false, true);
            wp_send_json_error(array('message' => 'Invalid response'));
        }
    }

    public function render_settings_page() {
        ?>
        <div class="wrap">
            <h1>🛡️ AI Fraud Detection Settings</h1>
            <form method="post" action="options.php">
                <?php settings_fields('wc_fraud_detection'); ?>
                <table class="form-table">
                    <tr>
                        <th><label for="wc_fraud_api_endpoint">API Endpoint</label></th>
                        <td>
                            <input type="text" id="wc_fraud_api_endpoint" name="wc_fraud_api_endpoint"
                                   value="<?php echo esc_attr(get_option('wc_fraud_api_endpoint', 'http://localhost:8000')); ?>"
                                   class="regular-text" placeholder="http://localhost:8000">
                            <p class="description">Base URL of your fraud detection API</p>
                        </td>
                    </tr>
                    <tr>
                        <th><label for="wc_fraud_api_key">API Key</label></th>
                        <td>
                            <input type="text" id="wc_fraud_api_key" name="wc_fraud_api_key"
                                   value="<?php echo esc_attr(get_option('wc_fraud_api_key', '')); ?>"
                                   class="regular-text" placeholder="Optional">
                        </td>
                    </tr>
                    <tr>
                        <th><label for="wc_fraud_threshold">Fraud Threshold</label></th>
                        <td>
                            <input type="number" id="wc_fraud_threshold" name="wc_fraud_threshold"
                                   value="<?php echo esc_attr(get_option('wc_fraud_threshold', '0.7')); ?>"
                                   step="0.01" min="0" max="1" class="small-text">
                            <p class="description">Confidence threshold (0.0 - 1.0)</p>
                        </td>
                    </tr>
                    <tr>
                        <th>Automatic Detection</th>
                        <td>
                            <label>
                                <input type="checkbox" name="wc_fraud_auto_check" value="1"
                                       <?php checked(get_option('wc_fraud_auto_check', '1'), '1'); ?>>
                                <strong>Enable automatic fraud detection on all new orders</strong>
                            </label>
                            <p class="description">Check every order automatically when placed (recommended)</p>
                        </td>
                    </tr>
                    <tr>
                        <th>Auto-Hold Orders</th>
                        <td>
                            <label>
                                <input type="checkbox" name="wc_fraud_auto_hold" value="1"
                                       <?php checked(get_option('wc_fraud_auto_hold', '1'), '1'); ?>>
                                <strong>Automatically place suspicious orders on hold</strong>
                            </label>
                            <p class="description">Orders flagged as fraud will be held for review</p>
                        </td>
                    </tr>
                    <tr>
                        <th>Email Alerts</th>
                        <td>
                            <label>
                                <input type="checkbox" name="wc_fraud_email_alerts" value="1"
                                       <?php checked(get_option('wc_fraud_email_alerts', '1'), '1'); ?>>
                                <strong>Send email alerts when fraud is detected</strong>
                            </label>
                            <p class="description">Notify admin at: <?php echo esc_html(get_option('admin_email')); ?></p>
                        </td>
                    </tr>
                </table>
                <?php submit_button('Save Settings'); ?>
            </form>

            <hr>

            <h2>🔍 Test API Connection</h2>
            <button type="button" class="button button-secondary" id="test-api-connection">Test Connection</button>
            <div id="api-test-result" style="margin-top: 10px;"></div>

            <script type="text/javascript">
            jQuery(document).ready(function($) {
                $('#test-api-connection').on('click', function() {
                    var endpoint = $('#wc_fraud_api_endpoint').val();
                    var resultDiv = $('#api-test-result');
                    resultDiv.html('<p>Testing connection...</p>');

                    $.ajax({
                        url: endpoint + '/api/v1/health',
                        method: 'GET',
                        timeout: 10000,
                        success: function(response) {
                            resultDiv.html('<div class="notice notice-success"><p>✅ <strong>Connection successful!</strong><br>Status: ' + response.status + '<br>Model loaded: ' + (response.model_loaded ? 'Yes' : 'No') + '</p></div>');
                        },
                        error: function(xhr, status, error) {
                            resultDiv.html('<div class="notice notice-error"><p>❌ <strong>Connection failed!</strong><br>Error: ' + error + '</p></div>');
                        }
                    });
                });
            });
            </script>
        </div>
        <?php
    }

    public function handle_csv_batch() {
        check_ajax_referer('csv_batch', 'nonce');

        $batch_json = isset($_POST['batch']) ? stripslashes($_POST['batch']) : '';
        $batch = json_decode($batch_json, true);

        if (!$batch || !is_array($batch)) {
            wp_send_json_error(array('message' => 'Invalid batch data'));
            return;
        }

        $api_endpoint = get_option('wc_fraud_api_endpoint', 'http://localhost:8000');
        $results = array();

        foreach ($batch as $row) {
            // Prepare transaction data from CSV row
            $transaction_data = array(
                'merchant_id' => get_bloginfo('name'),
                'amount' => floatval($row['amount'] ?? 0),
                'payment_method' => $row['payment_method'] ?? 'unknown',
                'user_id_hash' => 'csv_' . ($row['order_id'] ?? 'unknown'),
                'ip_hash' => 'csv_upload',
                'email_domain' => isset($row['customer_email']) ? substr(strrchr($row['customer_email'], '@'), 1) : 'unknown',
                'is_new_user' => ($row['is_new_customer'] ?? 'no') === 'yes',
                'device_type' => 'unknown',
                'billing_shipping_match' => true,
                'hour_of_day' => 12,
                'day_of_week' => 1,
                'items_count' => intval($row['items_count'] ?? 1)
            );

            // Call API
            $url = rtrim($api_endpoint, '/') . '/api/v1/predict';
            $response = wp_remote_post($url, array(
                'headers' => array('Content-Type' => 'application/json'),
                'body' => json_encode($transaction_data),
                'timeout' => 10,
                'sslverify' => false
            ));

            if (!is_wp_error($response)) {
                $body = wp_remote_retrieve_body($response);
                $fraud_result = json_decode($body, true);

                if ($fraud_result && isset($fraud_result['label'])) {
                    $results[] = array(
                        'order_id' => $row['order_id'] ?? 'N/A',
                        'amount' => $row['amount'] ?? 0,
                        'label' => $fraud_result['label'],
                        'confidence' => $fraud_result['confidence'],
                        'top_features' => $fraud_result['top_features'] ?? array()
                    );
                }
            }
        }

        wp_send_json_success(array('results' => $results));
    }

    public function auto_check_fraud($order_id) {
        error_log('=== AUTO CHECK TRIGGERED for order: ' . $order_id . ' ===');

        if (!$order_id) {
            error_log('Auto-check: No order ID');
            return;
        }

        // Check if automatic detection is enabled
        $auto_enabled = get_option('wc_fraud_auto_check', '1');
        error_log('Auto-check enabled setting: ' . $auto_enabled);
        if ($auto_enabled !== '1') {
            error_log('Auto-check: Disabled in settings');
            return;
        }

        try {
            $order = wc_get_order($order_id);
            if (!$order) {
                error_log('Auto-check: Order not found');
                return;
            }

            // Check if already checked
            $already_checked = $order->get_meta('_fraud_detection_checked');
            error_log('Auto-check: Already checked? ' . ($already_checked ? 'YES' : 'NO'));
            if ($already_checked) {
                error_log('Auto-check: Skipping - already checked');
                return;
            }

            error_log('Auto-check: Running fraud check...');
            // Run fraud check
            $this->run_fraud_check($order);
        } catch (Exception $e) {
            error_log('Auto fraud check error: ' . $e->getMessage());
        }
    }

    private function run_fraud_check($order) {
        try {
            $order_id = $order->get_id();

            // Add note that auto-check is running
            $order->add_order_note('🤖 Automatic fraud detection running...', false, false);

        // Get settings
        $api_endpoint = get_option('wc_fraud_api_endpoint', 'http://localhost:8000');
        $threshold = floatval(get_option('wc_fraud_threshold', 0.7));

        // Prepare transaction data (simplified for reliability)
        $billing_email = $order->get_billing_email();
        $email_domain = $billing_email ? substr(strrchr($billing_email, '@'), 1) : 'unknown';
        if (!$email_domain) {
            $email_domain = 'unknown';
        }

        $transaction_data = array(
            'merchant_id' => get_bloginfo('name'),
            'amount' => floatval($order->get_total()),
            'payment_method' => $order->get_payment_method() ?: 'unknown',
            'user_id_hash' => 'customer_' . ($order->get_customer_id() ?: 'guest'),
            'ip_hash' => 'ip_hash',
            'email_domain' => $email_domain,
            'is_new_user' => true,
            'device_type' => 'unknown',
            'billing_shipping_match' => true,
            'hour_of_day' => intval(current_time('G')),
            'day_of_week' => intval(current_time('N')) - 1,
            'items_count' => $order->get_item_count()
        );

        // Call API
        $url = rtrim($api_endpoint, '/') . '/api/v1/predict';
        error_log('Auto-check calling API: ' . $url);

        $response = wp_remote_post($url, array(
            'headers' => array('Content-Type' => 'application/json'),
            'body' => json_encode($transaction_data),
            'timeout' => 10,
            'sslverify' => false
        ));

        if (is_wp_error($response)) {
            $error_msg = $response->get_error_message();
            error_log('Auto-check API error: ' . $error_msg);
            $order->add_order_note('❌ Auto-check failed: ' . $error_msg, false, false);
            return;
        }

        $status_code = wp_remote_retrieve_response_code($response);
        $body = wp_remote_retrieve_body($response);
        error_log('Auto-check API response: ' . $status_code . ' - ' . $body);

        $fraud_result = json_decode($body, true);

        if (!$fraud_result) {
            error_log('Auto-check: Failed to decode JSON');
            $order->add_order_note('❌ Auto-check: Invalid API response', false, false);
            return;
        }

        if ($fraud_result && isset($fraud_result['label'])) {
            error_log('Auto-check: Got valid result - ' . $fraud_result['label']);

            $is_fraud = ($fraud_result['label'] === 'fraud');
            $confidence = isset($fraud_result['confidence']) ? ($fraud_result['confidence'] * 100) : 0;

            error_log('Auto-check: is_fraud=' . ($is_fraud ? 'true' : 'false') . ', confidence=' . $confidence);

            // Add result note FIRST (before save operations)
            // Check if fraud detected
            if ($is_fraud || $confidence >= ($threshold * 100)) {
                // FRAUD DETECTED!
                $auto_hold_enabled = get_option('wc_fraud_auto_hold', '1') === '1';
                $email_alerts_enabled = get_option('wc_fraud_email_alerts', '1') === '1';

                $order->add_order_note(
                    sprintf(
                        '🚨 <strong>FRAUD DETECTED!</strong> Confidence: %.2f%%%s',
                        $confidence,
                        $auto_hold_enabled ? ' - Order automatically placed on hold.' : ''
                    ),
                    true, // Customer visible
                    true  // Is note from admin
                );

                // Auto-hold the order (if enabled)
                if ($auto_hold_enabled && $order->get_status() !== 'on-hold') {
                    $order->update_status('on-hold', '🚨 Automatically held due to fraud detection');
                }

                // Send email notification to admin (if enabled)
                if ($email_alerts_enabled) {
                    $this->send_fraud_alert_email($order, $fraud_result);
                }

            } else {
                // Legitimate
                $order->add_order_note(
                    sprintf(
                        '✅ Fraud check passed (Confidence: %.2f%%)',
                        $confidence
                    ),
                    false,
                    false
                );
                error_log('Auto-check: Added legitimate note');
            }

            // Save results to meta (AFTER notes)
            $order->update_meta_data('_fraud_detection_result', $fraud_result);
            $order->update_meta_data('_fraud_detection_checked', current_time('mysql'));
            $order->update_meta_data('_fraud_auto_checked', 'yes');
            $order->save();
            error_log('Auto-check: Meta data saved');
        } else {
            error_log('Auto-check: No valid fraud_result or missing label');
        }
        } catch (Exception $e) {
            error_log('Run fraud check error: ' . $e->getMessage());
            if ($order) {
                $order->add_order_note('❌ Auto-check error: ' . $e->getMessage(), false, false);
            }
        }
    }

    private function send_fraud_alert_email($order, $fraud_result) {
        $admin_email = get_option('admin_email');
        $subject = '🚨 Fraud Alert - Order #' . $order->get_id();

        $message = sprintf(
            "Fraud detected on your WooCommerce store!\n\n" .
            "Order #: %s\n" .
            "Customer: %s\n" .
            "Email: %s\n" .
            "Amount: %s\n" .
            "Confidence: %.2f%%\n" .
            "Status: %s\n\n" .
            "View order: %s\n\n" .
            "This order has been automatically placed on hold for review.",
            $order->get_id(),
            $order->get_billing_first_name() . ' ' . $order->get_billing_last_name(),
            $order->get_billing_email(),
            $order->get_formatted_order_total(),
            $fraud_result['confidence'] * 100,
            $fraud_result['label'],
            admin_url('post.php?post=' . $order->get_id() . '&action=edit')
        );

        wp_mail($admin_email, $subject, $message);
    }

    public function add_fraud_meta_box() {
        add_meta_box(
            'wc_fraud_detection_manual',
            '🛡️ AI Fraud Detection',
            array($this, 'render_fraud_meta_box'),
            'woocommerce_page_wc-orders',
            'side',
            'high'
        );

        // Also add for legacy post-based orders
        add_meta_box(
            'wc_fraud_detection_manual',
            '🛡️ AI Fraud Detection',
            array($this, 'render_fraud_meta_box'),
            'shop_order',
            'side',
            'high'
        );
    }

    public function render_fraud_meta_box($post_or_order) {
        // Get order object
        if (is_a($post_or_order, 'WP_Post')) {
            $order = wc_get_order($post_or_order->ID);
            $order_id = $post_or_order->ID;
        } else {
            $order = $post_or_order;
            $order_id = $order->get_id();
        }

        if (!$order) {
            echo '<p>Unable to load order.</p>';
            return;
        }

        $fraud_result = $order->get_meta('_fraud_detection_result', true);
        $checked_time = $order->get_meta('_fraud_detection_checked', true);

        ?>
        <div class="fraud-detection-box">
            <?php if ($fraud_result): ?>
                <h4 style="margin-top:0;">Last Check: <?php echo esc_html($checked_time); ?></h4>

                <p><strong>Status:</strong>
                    <?php if ($fraud_result['label'] === 'fraud'): ?>
                        <span style="color: #dc3232;">🚨 FRAUD DETECTED</span>
                    <?php else: ?>
                        <span style="color: #46b450;">✅ Legitimate</span>
                    <?php endif; ?>
                </p>

                <p><strong>Confidence:</strong> <?php echo number_format($fraud_result['confidence'] * 100, 2); ?>%</p>

                <?php if (!empty($fraud_result['top_features'])): ?>
                    <p><strong>Top Factors:</strong></p>
                    <ul style="margin: 5px 0; padding-left: 20px; font-size: 11px;">
                        <?php foreach (array_slice($fraud_result['top_features'], 0, 3) as $feature): ?>
                            <li><?php echo esc_html($feature['feature']); ?>: <?php echo number_format($feature['contribution'], 2); ?></li>
                        <?php endforeach; ?>
                    </ul>
                <?php endif; ?>

                <p style="font-size: 11px; color: #666;">
                    <strong>Latency:</strong> <?php echo isset($fraud_result['latency_ms']) ? round($fraud_result['latency_ms']) : 'N/A'; ?>ms
                </p>

                <hr style="margin: 10px 0;">
            <?php endif; ?>

            <button type="button" id="fraud-check-btn" class="button button-primary" style="width: 100%;" data-order-id="<?php echo esc_attr($order_id); ?>">
                <?php echo $fraud_result ? '🔄 Re-check for Fraud' : '🔍 Check for Fraud'; ?>
            </button>
            <div id="fraud-check-status" style="margin-top: 10px; font-size: 12px; color: #666;"></div>

            <p style="font-size: 11px; color: #666; margin-top: 10px;">
                Click the button to analyze this order using AI fraud detection.
            </p>
        </div>
        <?php
    }

    public function handle_manual_check() {
        error_log('=== FRAUD CHECK STARTED ===');

        $order_id = isset($_POST['order_id']) ? intval($_POST['order_id']) : 0;
        error_log('Order ID: ' . $order_id);

        if (!$order_id) {
            error_log('ERROR: Invalid order ID');
            wp_die('Invalid order ID');
        }

        check_admin_referer('check_fraud_' . $order_id);
        error_log('Nonce verified');

        $order = wc_get_order($order_id);
        if (!$order) {
            error_log('ERROR: Order not found');
            wp_die('Order not found');
        }

        // Get settings
        $api_endpoint = get_option('wc_fraud_api_endpoint', 'http://localhost:8000');
        $api_key = get_option('wc_fraud_api_key', '');
        error_log('API Endpoint: ' . $api_endpoint);

        // Add immediate order note to show button was clicked
        $order->add_order_note('🔄 Fraud check initiated...', false, true);

        // Prepare transaction data
        $transaction_data = $this->prepare_transaction_data($order);
        error_log('Transaction data prepared: ' . print_r($transaction_data, true));

        // Call API
        $fraud_result = $this->call_fraud_api($api_endpoint, $api_key, $transaction_data);
        error_log('API Result: ' . print_r($fraud_result, true));

        if ($fraud_result && isset($fraud_result['label'])) {
            // Save results
            $order->update_meta_data('_fraud_detection_result', $fraud_result);
            $order->update_meta_data('_fraud_detection_checked', current_time('mysql'));
            $order->save();
            error_log('Results saved to order meta');

            // Add order note
            $order->add_order_note(
                sprintf(
                    '🛡️ Fraud check completed: %s (Confidence: %.2f%%)',
                    $fraud_result['label'] === 'fraud' ? '🚨 FRAUD' : '✅ Legitimate',
                    $fraud_result['confidence'] * 100
                ),
                false,
                true
            );
            error_log('Order note added - SUCCESS');

            // Set admin notice
            set_transient('wc_fraud_check_message', 'success', 30);
        } else {
            error_log('ERROR: API call failed or invalid response');
            $order->add_order_note('❌ Fraud check failed - API error', false, true);
            set_transient('wc_fraud_check_message', 'error', 30);
        }

        // Redirect back
        $redirect_url = wp_get_referer();
        error_log('Redirecting to: ' . $redirect_url);
        wp_redirect($redirect_url);
        exit;
    }

    private function prepare_transaction_data($order) {
        $customer = $order->get_user();
        $billing = $order->get_address('billing');
        $shipping = $order->get_address('shipping');

        $order_date = $order->get_date_created();
        $hour_of_day = intval($order_date->format('G'));
        $day_of_week = intval($order_date->format('N')) - 1;

        $billing_shipping_match = (
            $billing['address_1'] === $shipping['address_1'] &&
            $billing['city'] === $shipping['city'] &&
            $billing['postcode'] === $shipping['postcode']
        );

        $is_new_user = !$customer || $order->get_customer_order_count() <= 1;

        return array(
            'merchant_id' => get_bloginfo('name'),
            'amount' => floatval($order->get_total()),
            'payment_method' => $order->get_payment_method(),
            'user_id_hash' => $customer ? hash('sha256', strval($customer->ID)) : 'guest',
            'ip_hash' => hash('sha256', $order->get_customer_ip_address() ?: 'unknown'),
            'email_domain' => substr(strrchr($billing['email'], '@'), 1) ?: 'unknown',
            'is_new_user' => $is_new_user,
            'device_type' => 'unknown',
            'billing_shipping_match' => $billing_shipping_match,
            'hour_of_day' => $hour_of_day,
            'day_of_week' => $day_of_week,
            'items_count' => $order->get_item_count()
        );
    }

    private function call_fraud_api($endpoint, $api_key, $data) {
        $url = rtrim($endpoint, '/') . '/api/v1/predict';
        error_log('Making API request to: ' . $url);

        $headers = array('Content-Type' => 'application/json');
        if (!empty($api_key)) {
            $headers['X-API-Key'] = $api_key;
        }

        $body_json = json_encode($data);
        error_log('Request body: ' . $body_json);

        $response = wp_remote_post($url, array(
            'headers' => $headers,
            'body' => $body_json,
            'timeout' => 10,
            'sslverify' => false
        ));

        if (is_wp_error($response)) {
            error_log('Fraud API WP Error: ' . $response->get_error_message());
            return null;
        }

        $status_code = wp_remote_retrieve_response_code($response);
        $body = wp_remote_retrieve_body($response);

        error_log('API Response Status: ' . $status_code);
        error_log('API Response Body: ' . $body);

        if ($status_code !== 200) {
            error_log('API returned non-200 status: ' . $status_code);
            return null;
        }

        $result = json_decode($body, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            error_log('JSON decode error: ' . json_last_error_msg());
            return null;
        }

        return $result;
    }
}

WC_AI_Fraud_Detection_Manual::get_instance();
