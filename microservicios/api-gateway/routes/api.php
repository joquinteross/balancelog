<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\UsuariosGatewayController;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| is assigned the "api" middleware group. Enjoy building your API!
|
*/

#Ruta del microservicio de usuarios


Route::post('/auth/register', [UsuariosGatewayController::class, 'register']);
Route::post('/auth/login', [UsuariosGatewayController::class, 'login']);
Route::post('/auth/logout', [UsuariosGatewayController::class, 'logout']);
Route::post('/auth/password', [UsuariosGatewayController::class, 'changePassword']);
Route::get('/auth/me', [UsuariosGatewayController::class, 'me']);

