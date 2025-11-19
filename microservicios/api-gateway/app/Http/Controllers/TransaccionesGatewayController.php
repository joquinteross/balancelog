<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class TransaccionesGatewayController extends Controller
{
    protected $baseUrl;
    protected $apiKey;

    public function __construct()
    {
        $this->baseUrl = env('TRANSACCIONES_URL');
        $this->apiKey  = env('API_KEY');
    }
    public function crear(Request $request)
    {
        $url = $this->baseUrl . '/transacciones';

        $response = Http::withHeaders([
            'X-API-KEY' => $this->apiKey,
        ])->post($url, $request->all());

        return response()->json($response->json(), $response->status());
    }

    public function listar($user_id)
    {
        $url = $this->baseUrl . "/transacciones/{$user_id}";

        $response = Http::withHeaders([
            'X-API-KEY' => $this->apiKey,
        ])->get($url);

        return response()->json($response->json(), $response->status());
    }

    public function actualizar($id, Request $request)
    {
        $url = $this->baseUrl . "/transacciones/{$id}";

        $response = Http::withHeaders([
            'X-API-KEY' => $this->apiKey,
        ])->put($url, $request->all());

        return response()->json($response->json(), $response->status());
    }

    public function eliminar($id)
    {
        $url = $this->baseUrl . "/transacciones/{$id}";

        $response = Http::withHeaders([
            'X-API-KEY' => $this->apiKey,
        ])->delete($url);

        return response()->json($response->json(), $response->status());
    }

    public function resumenMensual($user_id, $mes)
    {
        $url = $this->baseUrl . "/transacciones/resumen/{$user_id}/{$mes}";

        $response = Http::withHeaders([
            'X-API-KEY' => $this->apiKey,
        ])->get($url);

        return response()->json($response->json(), $response->status());
    }
}
