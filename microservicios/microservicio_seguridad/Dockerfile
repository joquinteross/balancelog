FROM php:8.1-cli

# Extensiones necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    unzip \
    libzip-dev \
    libonig-dev \
    libxml2-dev \
 && docker-php-ext-install pdo_mysql \
 && rm -rf /var/lib/apt/lists/*

# Instalar Composer
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

WORKDIR /var/www/html

# Copiamos solo composer primero (para cache de dependencias)
COPY composer.json composer.lock* ./

RUN composer install --no-dev --optimize-autoloader --no-interaction --no-progress || true

# Copiamos el resto del proyecto
COPY . .

# Generar key si no existe
RUN php artisan key:generate --force || true

EXPOSE 8000

CMD ["php", "artisan", "serve", "--host=0.0.0.0", "--port=8000"]
