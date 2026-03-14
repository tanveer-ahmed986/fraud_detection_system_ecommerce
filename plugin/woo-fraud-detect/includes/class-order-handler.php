<?php
defined('ABSPATH') || exit;

class WFD_Order_Handler {
    public static function init(): void {
        add_action('woocommerce_checkout_order_processed', [self::class, 'check_order'], 10, 3);
    }

    public static function check_order(int $order_id, array $posted_data, WC_Order $order): void {
        $client = new WFD_API_Client();

        $transaction = [
            'merchant_id' => get_option('blogname', 'woocommerce'),
            'amount' => (float) $order->get_total(),
            'payment_method' => self::map_payment_method($order->get_payment_method()),
            'user_id_hash' => hash('sha256', (string) $order->get_customer_id()),
            'ip_hash' => hash('sha256', $order->get_customer_ip_address()),
            'email_domain' => explode('@', $order->get_billing_email())[1] ?? 'unknown',
            'is_new_user' => $order->get_customer_id() === 0,
            'device_type' => self::detect_device(),
            'billing_shipping_match' => self::check_address_match($order),
            'hour_of_day' => (int) current_time('G'),
            'day_of_week' => (int) current_time('w'),
            'items_count' => $order->get_item_count(),
        ];

        $result = $client->predict($transaction);

        if (is_wp_error($result)) {
            $order->add_order_note('Fraud check failed: ' . $result->get_error_message());
            if ((float) $order->get_total() >= 50.0) {
                $order->update_status('on-hold', 'Fraud API unavailable — held for manual review');
            }
            return;
        }

        $order->update_meta_data('_fraud_label', $result['label']);
        $order->update_meta_data('_fraud_confidence', $result['confidence']);
        $order->update_meta_data('_fraud_features', wp_json_encode($result['top_features'] ?? []));
        $order->save();

        $confidence_pct = round($result['confidence'] * 100, 1);
        $order->add_order_note(sprintf(
            'Fraud check: %s (%.1f%% confidence). Top factors: %s',
            strtoupper($result['label']),
            $confidence_pct,
            implode(', ', array_map(fn($f) => $f['feature'], $result['top_features'] ?? []))
        ));

        if ($result['label'] === 'fraud' && get_option('wfd_auto_hold', 1)) {
            $order->update_status('on-hold', 'Flagged as potential fraud');

            if (get_option('wfd_notifications', 1)) {
                wp_mail(
                    get_option('admin_email'),
                    "Fraud Alert: Order #{$order_id}",
                    sprintf("Order #%d (%.2f) flagged as fraud with %.1f%% confidence.", $order_id, $order->get_total(), $confidence_pct)
                );
            }
        }
    }

    private static function map_payment_method(string $method): string {
        $map = [
            'stripe' => 'credit_card', 'bacs' => 'bank_transfer',
            'paypal' => 'paypal', 'cod' => 'bank_transfer',
        ];
        return $map[$method] ?? 'credit_card';
    }

    private static function detect_device(): string {
        $ua = strtolower($_SERVER['HTTP_USER_AGENT'] ?? '');
        if (str_contains($ua, 'mobile') || str_contains($ua, 'android')) return 'mobile';
        if (str_contains($ua, 'tablet') || str_contains($ua, 'ipad')) return 'tablet';
        return 'desktop';
    }

    private static function check_address_match(WC_Order $order): bool {
        return $order->get_billing_address_1() === $order->get_shipping_address_1()
            && $order->get_billing_city() === $order->get_shipping_city()
            && $order->get_billing_postcode() === $order->get_shipping_postcode();
    }
}
