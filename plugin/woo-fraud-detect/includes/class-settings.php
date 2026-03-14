<?php
defined('ABSPATH') || exit;

class WFD_Settings {
    public static function init(): void {
        add_action('admin_menu', [self::class, 'add_menu']);
        add_action('admin_init', [self::class, 'register_settings']);
    }

    public static function add_menu(): void {
        add_submenu_page(
            'woocommerce',
            'Fraud Detection',
            'Fraud Detection',
            'manage_woocommerce',
            'wfd-settings',
            [self::class, 'render_page']
        );
    }

    public static function register_settings(): void {
        register_setting('wfd_settings', 'wfd_api_endpoint');
        register_setting('wfd_settings', 'wfd_api_timeout');
        register_setting('wfd_settings', 'wfd_fraud_threshold');
        register_setting('wfd_settings', 'wfd_auto_hold');
        register_setting('wfd_settings', 'wfd_notifications');
    }

    public static function render_page(): void {
        $client = new WFD_API_Client();
        $health = $client->health();
        ?>
        <div class="wrap">
            <h1>Fraud Detection Settings</h1>
            <?php if (is_wp_error($health)): ?>
                <div class="notice notice-error"><p>API not reachable: <?php echo esc_html($health->get_error_message()); ?></p></div>
            <?php else: ?>
                <div class="notice notice-success"><p>API connected — Model: <?php echo esc_html($health['model_version'] ?? 'unknown'); ?></p></div>
            <?php endif; ?>
            <form method="post" action="options.php">
                <?php settings_fields('wfd_settings'); ?>
                <table class="form-table">
                    <tr><th>API Endpoint</th><td><input type="url" name="wfd_api_endpoint" value="<?php echo esc_attr(get_option('wfd_api_endpoint', 'http://localhost:8000')); ?>" class="regular-text" /></td></tr>
                    <tr><th>Timeout (seconds)</th><td><input type="number" name="wfd_api_timeout" value="<?php echo esc_attr(get_option('wfd_api_timeout', 5)); ?>" min="1" max="30" /></td></tr>
                    <tr><th>Fraud Threshold</th><td><input type="number" name="wfd_fraud_threshold" value="<?php echo esc_attr(get_option('wfd_fraud_threshold', 0.5)); ?>" step="0.01" min="0" max="1" /></td></tr>
                    <tr><th>Auto-hold Fraud Orders</th><td><input type="checkbox" name="wfd_auto_hold" value="1" <?php checked(get_option('wfd_auto_hold', 1)); ?> /></td></tr>
                    <tr><th>Email Notifications</th><td><input type="checkbox" name="wfd_notifications" value="1" <?php checked(get_option('wfd_notifications', 1)); ?> /></td></tr>
                </table>
                <?php submit_button(); ?>
            </form>
        </div>
        <?php
    }
}
