<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class ReportesGatewayController extends Controller
{
    protected $baseUrl;
    protected $apiKey;

    public function __construct()
    {
        $this->baseUrl = env('REPORTES_URL');        // http://localhost:5004
        $this->apiKey  = env('API_KEY');
    }

    public function pdf($user_id, $mes)
    {
        $url = $this->baseUrl . "/reportes/{$user_id}/{$mes}/pdf";

        $response = Http::withHeaders([
            'X-API-KEY' => $this->apiKey,
        ])->get($url);

        return response($response->body(), $response->status())
            ->withHeaders([
                'Content-Type'        => $response->header('Content-Type'),
                'Content-Disposition' => $response->header('Content-Disposition'),
            ]);
    }

    public function excel($user_id, $mes)
    {
        $url = $this->baseUrl . "/reportes/{$user_id}/{$mes}/excel";

        $response = Http::withHeaders([
            'X-API-KEY' => $this->apiKey,
        ])->get($url);

        return response($response->body(), $response->status())
            ->withHeaders([
                'Content-Type'        => $response->header('Content-Type'),
                'Content-Disposition' => $response->header('Content-Disposition'),
            ]);
    }
}
