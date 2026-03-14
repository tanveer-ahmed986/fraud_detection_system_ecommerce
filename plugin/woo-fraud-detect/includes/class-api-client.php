<?php
defined('ABSPATH') || exit;

class WFD_API_Client {
    private string $endpoint;
    private int $timeout;

    public function __construct() {
        $this->endpoint = rtrim(get_option('wfd_api_endpoint', 'http://localhost:8000'), '/');
        $this->timeout = (int) get_option('wfd_api_timeout', 5);
    }

    public function predict(array $transaction_data): array|WP_Error {
        $response = wp_remote_post("{$this->endpoint}/api/v1/predict", [
            'timeout' => $this->timeout,
            'headers' => ['Content-Type' => 'application/json'],
            'body' => wp_json_encode($transaction_data),
        ]);

        if (is_wp_error($response)) {
            return $response;
        }

        $code = wp_remote_retrieve_response_code($response);
        $body = json_decode(wp_remote_retrieve_body($response), true);

        if ($code !== 200 || !$body) {
            return new WP_Error('api_error', 'Fraud detection API returned an error', [
                'status' => $code,
                'body' => $body,
            ]);
        }

        return $body;
    }

    public function health(): array|WP_Error {
        $response = wp_remote_get("{$this->endpoint}/api/v1/health", [
            'timeout' => $this->timeout,
        ]);

        if (is_wp_error($response)) {
            return $response;
        }

        return json_decode(wp_remote_retrieve_body($response), true) ?: [];
    }
}
