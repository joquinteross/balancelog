<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class UsuariosGatewayController extends Controller
{
    protected $baseUrl;
    protected $apiKey;

    public function __construct()
    {
        $this->baseUrl = env('USUARIOS_URL');
        $this->apiKey = env('API_KEY');
    }

    #Registrar usuario
    public function register(Request $request)
    {
        $url = $this->baseUrl . '/api/register';

        $response = Http::withHeaders([
            'X-API-KEY' => $this->apiKey,
        ])->post($url, $request->all());

        return response()->json($response->json(), $response->status());
    }

    #Logear usuario
    public function login(Request $request)
    {
        $url = $this->baseUrl . '/api/login';

        $response = Http::withHeaders([
            'X-API-KEY' => $this->apiKey,
        ])->post($url, $request->all());

        return response()->json($response->json(), $response->status());
    }

    #Cerra cesion

    public function logout(Request $request)
    {
        $url = $this->baseUrl . '/api/logout';

        $response = Http::withHeaders([
            'X-API-KEY' => $this->apiKey,
            'Authorization' => $request->header('Authorization'),
        ])->post($url);

        return response()->json($response->json(), $response->status());
    }


    #cambiar contraseña
    public function changePassword(Request $request)
    {
        $url = $this->baseUrl . '/api/password';

        $response = Http::withHeaders([
            'X-API-KEY' => $this->apiKey,
            'Authorization' => $request->header('Authorization'),
        ])->post($url, $request->all());

        return response()->json($response->json(), $response->status());
    }


    #test me
    public function me(Request $request)
    {

        $token = $request->bearerToken();

        
        if (!$token) {
            return response()->json(['message' => 'No esta autenticado'], 401);
        }
        $url = $this->baseUrl . '/api/me';

        $response = Http::withHeaders([
            'X-API-KEY' => $this->apiKey,
            'Authorization' => $request->header('Authorization'),
        ])->get($url);

        return response()->json($response->json(), $response->status());
    }
}
