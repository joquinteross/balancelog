<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\UserController;

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


Route::post('/register', [UserController::class,'create_user']);
Route::post('/login', [UserController::class,'login']);
Route::group(['middleware' => 'auth:sanctum'], function () {
    Route::post('/logout', [UserController::class,'logout']);
    Route::post('/password', [UserController::class,'change_password']);
    Route::get('/me', [UserController::class, 'me']);
});



