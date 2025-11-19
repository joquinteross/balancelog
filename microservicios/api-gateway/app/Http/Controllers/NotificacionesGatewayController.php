<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class NotificacionesGatewayController extends Controller
{
    protected $baseUrl;
    protected $apiKey;

    public function __construct()
    {
        $this->baseUrl = env('NOTIFICACIONES_URL');  // http://localhost:5003
        $this->apiKey  = env('API_KEY');
    }

    public function estado($user_id, $mes)
    {
        $url = $this->baseUrl . "/notificaciones/{$user_id}/{$mes}";

        $response = Http::withHeaders([
            'X-API-KEY' => $this->apiKey,
        ])->get($url);

        return response()->json($response->json(), $response->status());
    }
}
