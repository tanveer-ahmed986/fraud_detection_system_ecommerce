<?php
/**
 * Plugin Name: WooCommerce Fraud Detection
 * Description: Real-time fraud detection for WooCommerce orders using ML API
 * Version: 1.0.0
 * Author: Fraud Detection System
 * Requires PHP: 8.0
 * WC requires at least: 8.0
 */

defined('ABSPATH') || exit;

define('WFD_VERSION', '1.0.0');
define('WFD_PLUGIN_DIR', plugin_dir_path(__FILE__));

require_once WFD_PLUGIN_DIR . 'includes/class-api-client.php';
require_once WFD_PLUGIN_DIR . 'includes/class-settings.php';
require_once WFD_PLUGIN_DIR . 'includes/class-order-handler.php';

add_action('plugins_loaded', function () {
    if (!class_exists('WooCommerce')) {
        add_action('admin_notices', function () {
            echo '<div class="error"><p>WooCommerce Fraud Detection requires WooCommerce.</p></div>';
        });
        return;
    }

    WFD_Settings::init();
    WFD_Order_Handler::init();
});
