<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class PresupuestosGatewayController extends Controller
{
    protected $baseUrl;
    protected $apiKey;

    public function __construct()
    {
        $this->baseUrl = env('PRESUPUESTOS_URL');  
        $this->apiKey  = env('API_KEY');
    }

    public function crear(Request $request)
    {
        $url = $this->baseUrl . '/presupuesto';

        $response = Http::withHeaders([
            'X-API-KEY' => $this->apiKey,
        ])->post($url, $request->all());

        return response()->json($response->json(), $response->status());
    }

    public function ver($user_id)
    {
        $url = $this->baseUrl . "/presupuesto/{$user_id}";

        $response = Http::withHeaders([
            'X-API-KEY' => $this->apiKey,
        ])->get($url);

        return response()->json($response->json(), $response->status());
    }

    public function actualizar($user_id, Request $request)
    {
        $url = $this->baseUrl . "/presupuesto/{$user_id}";

        $response = Http::withHeaders([
            'X-API-KEY' => $this->apiKey,
        ])->put($url, $request->all());

        return response()->json($response->json(), $response->status());
    }
}
