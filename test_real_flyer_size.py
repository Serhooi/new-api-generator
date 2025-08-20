#!/usr/bin/env python3
"""
Тестируем размер PNG для реального флаера
"""

import sys
sys.path.append('.')

from app import convert_svg_to_png_improved, create_preview_svg
import os

def test_simple_vs_complex_svg():
    """Сравниваем размеры простого и сложного SVG"""
    
    print("🧪 ТЕСТ РАЗМЕРОВ PNG ДЛЯ РАЗНЫХ SVG")
    print("=" * 45)
    
    # 1. Простой SVG (как в тесте)
    simple_svg = '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
        <rect width="400" height="300" fill="#f0f8ff"/>
        <text x="200" y="150" text-anchor="middle" font-size="24" fill="#1976d2">Simple Test</text>
    </svg>'''
    
    # 2. Сложный реалистичный флаер
    complex_svg = '''<svg width="1080" height="1350" xmlns="http://www.w3.org/2000/svg">
        <!-- Фон с градиентом -->
        <defs>
            <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#1976d2;stop-opacity:1" />
                <stop offset="50%" style="stop-color:#42a5f5;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#e3f2fd;stop-opacity:1" />
            </linearGradient>
            <radialGradient id="photoGrad" cx="50%" cy="50%" r="50%">
                <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0.8" />
                <stop offset="100%" style="stop-color:#000000;stop-opacity:0.2" />
            </radialGradient>
        </defs>
        
        <!-- Основной фон -->
        <rect width="1080" height="1350" fill="url(#bgGrad)"/>
        
        <!-- Заголовок -->
        <rect x="40" y="40" width="1000" height="180" fill="#ffffff" rx="20" opacity="0.95"/>
        <text x="540" y="110" text-anchor="middle" font-size="48" fill="#1976d2" font-weight="bold">LUXURY REAL ESTATE</text>
        <text x="540" y="160" text-anchor="middle" font-size="24" fill="#666">Premium Properties Available</text>
        
        <!-- Основное изображение недвижимости -->
        <rect x="80" y="260" width="920" height="500" fill="#f5f5f5" stroke="#ddd" stroke-width="3" rx="15"/>
        <rect x="100" y="280" width="880" height="460" fill="url(#photoGrad)" rx="10"/>
        <text x="540" y="520" text-anchor="middle" font-size="32" fill="#333" font-weight="bold">STUNNING PROPERTY</text>
        
        <!-- Детали недвижимости -->
        <rect x="80" y="800" width="920" height="200" fill="#ffffff" rx="15" opacity="0.95"/>
        
        <!-- Цена -->
        <rect x="120" y="830" width="280" height="80" fill="#4caf50" rx="10"/>
        <text x="260" y="880" text-anchor="middle" font-size="36" fill="white" font-weight="bold">$1,250,000</text>
        
        <!-- Характеристики -->
        <rect x="420" y="830" width="160" height="80" fill="#2196f3" rx="10"/>
        <text x="500" y="860" text-anchor="middle" font-size="18" fill="white" font-weight="bold">5 BEDS</text>
        <text x="500" y="885" text-anchor="middle" font-size="14" fill="white">Bedrooms</text>
        
        <rect x="600" y="830" width="160" height="80" fill="#ff9800" rx="10"/>
        <text x="680" y="860" text-anchor="middle" font-size="18" fill="white" font-weight="bold">4 BATHS</text>
        <text x="680" y="885" text-anchor="middle" font-size="14" fill="white">Bathrooms</text>
        
        <rect x="780" y="830" width="180" height="80" fill="#9c27b0" rx="10"/>
        <text x="870" y="860" text-anchor="middle" font-size="18" fill="white" font-weight="bold">3,500 SQ FT</text>
        <text x="870" y="885" text-anchor="middle" font-size="14" fill="white">Living Space</text>
        
        <!-- Адрес -->
        <text x="540" y="950" text-anchor="middle" font-size="28" fill="#333" font-weight="bold">123 Luxury Avenue, Beverly Hills, CA 90210</text>
        
        <!-- Дополнительные детали -->
        <rect x="80" y="1020" width="920" height="120" fill="#f8f9fa" rx="15" stroke="#e0e0e0" stroke-width="2"/>
        <text x="540" y="1060" text-anchor="middle" font-size="20" fill="#555">✓ Ocean View  ✓ Private Pool  ✓ 3-Car Garage  ✓ Smart Home</text>
        <text x="540" y="1090" text-anchor="middle" font-size="18" fill="#777">✓ Gourmet Kitchen  ✓ Wine Cellar  ✓ Home Theater</text>
        <text x="540" y="1120" text-anchor="middle" font-size="16" fill="#999">Move-in Ready • Recently Renovated • Premium Location</text>
        
        <!-- Контактная информация -->
        <rect x="80" y="1160" width="920" height="150" fill="#1976d2" rx="15"/>
        <text x="540" y="1200" text-anchor="middle" font-size="24" fill="white" font-weight="bold">CONTACT PREMIUM REALTY TODAY</text>
        <text x="540" y="1240" text-anchor="middle" font-size="32" fill="#ffeb3b" font-weight="bold">(555) 123-LUXURY</text>
        <text x="540" y="1270" text-anchor="middle" font-size="18" fill="#e3f2fd">info@premiumrealty.com</text>
        <text x="540" y="1295" text-anchor="middle" font-size="16" fill="#bbdefb">www.premiumrealty.com</text>
        
        <!-- Декоративные элементы -->
        <circle cx="100" cy="100" r="30" fill="#ffeb3b" opacity="0.7"/>
        <circle cx="980" cy="100" r="25" fill="#4caf50" opacity="0.6"/>
        <circle cx="100" cy="1250" r="35" fill="#ff5722" opacity="0.5"/>
        <circle cx="980" cy="1250" r="28" fill="#9c27b0" opacity="0.6"/>
    </svg>'''
    
    # Тестируем простой SVG
    print("1️⃣ Простой SVG (400x300):")
    success1 = convert_svg_to_png_improved(simple_svg, 'test_simple.png', 400, 300)
    if success1 and os.path.exists('test_simple.png'):
        size1 = os.path.getsize('test_simple.png')
        print(f"   📊 Размер: {size1:,} bytes ({size1/1024:.1f} KB)")
        os.remove('test_simple.png')
    
    # Тестируем сложный SVG
    print("\n2️⃣ Сложный флаер (1080x1350):")
    success2 = convert_svg_to_png_improved(complex_svg, 'test_complex.png', 1080, 1350)
    if success2 and os.path.exists('test_complex.png'):
        size2 = os.path.getsize('test_complex.png')
        print(f"   📊 Размер: {size2:,} bytes ({size2/1024:.1f} KB)")
        
        if size2 > 100000:  # Больше 100KB
            print("   ✅ Размер соответствует сложному флаеру!")
        else:
            print("   ⚠️ Размер маленький для сложного флаера")
        
        os.remove('test_complex.png')
    
    # Тестируем с реальными dyno полями
    print("\n3️⃣ Флаер с dyno полями:")
    dyno_svg = '''<svg width="1080" height="1350" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#1976d2"/>
                <stop offset="100%" style="stop-color:#e3f2fd"/>
            </linearGradient>
        </defs>
        <rect width="1080" height="1350" fill="url(#bg)"/>
        <rect x="40" y="40" width="1000" height="1270" fill="white" rx="20" opacity="0.95"/>
        
        <!-- Заголовок агента -->
        <text x="540" y="120" text-anchor="middle" font-size="42" fill="#1976d2" font-weight="bold">{{dyno.agentName}}</text>
        <text x="540" y="160" text-anchor="middle" font-size="20" fill="#666">Licensed Real Estate Professional</text>
        
        <!-- Изображение недвижимости -->
        <rect x="80" y="200" width="920" height="400" fill="#f0f0f0" stroke="#ddd" stroke-width="2" rx="10"/>
        <text x="540" y="410" text-anchor="middle" font-size="16" fill="#999">Property Image Placeholder</text>
        
        <!-- Адрес -->
        <text x="540" y="660" text-anchor="middle" font-size="32" fill="#333" font-weight="bold">{{dyno.propertyAddress}}</text>
        
        <!-- Цена -->
        <rect x="200" y="700" width="680" height="100" fill="#4caf50" rx="15"/>
        <text x="540" y="760" text-anchor="middle" font-size="48" fill="white" font-weight="bold">{{dyno.price}}</text>
        
        <!-- Характеристики -->
        <rect x="120" y="830" width="200" height="80" fill="#2196f3" rx="10"/>
        <text x="220" y="880" text-anchor="middle" font-size="24" fill="white" font-weight="bold">{{dyno.bedrooms}} BED</text>
        
        <rect x="340" y="830" width="200" height="80" fill="#ff9800" rx="10"/>
        <text x="440" y="880" text-anchor="middle" font-size="24" fill="white" font-weight="bold">{{dyno.bathrooms}} BATH</text>
        
        <rect x="560" y="830" width="200" height="80" fill="#9c27b0" rx="10"/>
        <text x="660" y="880" text-anchor="middle" font-size="20" fill="white" font-weight="bold">{{dyno.sqft}} SQ FT</text>
        
        <!-- Контакты -->
        <rect x="80" y="950" width="920" height="120" fill="#1976d2" rx="15"/>
        <text x="540" y="990" text-anchor="middle" font-size="24" fill="white" font-weight="bold">Contact Me Today!</text>
        <text x="540" y="1025" text-anchor="middle" font-size="28" fill="#ffeb3b" font-weight="bold">{{dyno.agentPhone}}</text>
        <text x="540" y="1055" text-anchor="middle" font-size="18" fill="#e3f2fd">{{dyno.agentEmail}}</text>
        
        <!-- Дополнительная информация -->
        <text x="540" y="1120" text-anchor="middle" font-size="18" fill="#555">Open House: {{dyno.openHouseDate}}</text>
        <text x="540" y="1150" text-anchor="middle" font-size="18" fill="#555">Time: {{dyno.openHouseTime}}</text>
        
        <!-- Декоративные элементы -->
        <circle cx="100" cy="100" r="25" fill="#ffeb3b" opacity="0.8"/>
        <circle cx="980" cy="100" r="20" fill="#4caf50" opacity="0.7"/>
        <circle cx="100" cy="1250" r="30" fill="#ff5722" opacity="0.6"/>
        <circle cx="980" cy="1250" r="25" fill="#9c27b0" opacity="0.7"/>
    </svg>'''
    
    # Заменяем dyno поля
    preview_svg = create_preview_svg(dyno_svg)
    
    success3 = convert_svg_to_png_improved(preview_svg, 'test_dyno.png', 1080, 1350)
    if success3 and os.path.exists('test_dyno.png'):
        size3 = os.path.getsize('test_dyno.png')
        print(f"   📊 Размер: {size3:,} bytes ({size3/1024:.1f} KB)")
        
        if size3 > 50000:  # Больше 50KB
            print("   ✅ Размер нормальный для флаера с данными!")
        else:
            print("   ⚠️ Размер все еще маленький")
        
        os.remove('test_dyno.png')
    
    print("\n" + "=" * 45)
    print("📋 АНАЛИЗ РАЗМЕРОВ:")
    print("• Простые SVG → маленькие PNG (10-20KB)")
    print("• Сложные SVG с градиентами → средние PNG (50-200KB)")
    print("• SVG с фотографиями → большие PNG (500KB-2MB)")
    print("• Текущие тесты используют простые SVG без фото")

if __name__ == "__main__":
    test_simple_vs_complex_svg()