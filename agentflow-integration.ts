// 🔗 AGENTFLOW INTEGRATION - TypeScript код для интеграции с API

// ===== ТИПЫ ДАННЫХ =====

interface Template {
  id: string;
  name: string;
  category: string;
  template_role: 'main' | 'photo';
  preview_url: string;
}

interface DynoReplacements {
  'dyno.agentName'?: string;
  'dyno.propertyAddress'?: string;
  'dyno.price'?: string;
  'dyno.bedrooms'?: string;
  'dyno.bathrooms'?: string;
  'dyno.sqft'?: string;
  'dyno.agentPhone'?: string;
  'dyno.agentEmail'?: string;
  'dyno.openHouseDate'?: string;
  'dyno.openHouseTime'?: string;
  'dyno.agentPhoto'?: string;
  'dyno.companyLogo'?: string;
  'dyno.propertyImage'?: string;
}

interface SlideRequest {
  templateId: string;
  replacements: DynoReplacements;
  imagePath: string;
}

interface CarouselRequest {
  name: string;
  slides: SlideRequest[];
}

interface SlideResponse {
  slide_number: number;
  status: 'pending' | 'generating' | 'completed' | 'error';
  image_url: string | null;
}

interface CarouselResponse {
  carousel_id: string;
  status: 'pending' | 'generating' | 'completed' | 'error';
  slides: SlideResponse[];
}

// ===== API КЛИЕНТ =====

class SVGTemplateAPI {
  private baseUrl: string;

  constructor(baseUrl: string = 'https://your-api.onrender.com') {
    this.baseUrl = baseUrl;
  }

  // 🔍 Получение всех доступных шаблонов
  async getTemplates(): Promise<Template[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/templates/all-previews`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.templates;
    } catch (error) {
      console.error('Error fetching templates:', error);
      throw error;
    }
  }

  // 🎠 Создание и генерация карусели (рекомендуемый метод)
  async createAndGenerateCarousel(request: CarouselRequest): Promise<{ carousel_id: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/carousel/create-and-generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return { carousel_id: data.carousel_id };
    } catch (error) {
      console.error('Error creating carousel:', error);
      throw error;
    }
  }

  // 📊 Проверка статуса карусели и получение URL
  async getCarouselStatus(carouselId: string): Promise<CarouselResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/carousel/${carouselId}/slides`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching carousel status:', error);
      throw error;
    }
  }

  // ⏳ Ожидание завершения генерации с polling
  async waitForCarouselCompletion(
    carouselId: string, 
    maxAttempts: number = 30,
    intervalMs: number = 2000
  ): Promise<CarouselResponse> {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      const status = await this.getCarouselStatus(carouselId);
      
      if (status.status === 'completed') {
        return status;
      }
      
      if (status.status === 'error') {
        throw new Error('Carousel generation failed');
      }
      
      // Ждем перед следующей проверкой
      await new Promise(resolve => setTimeout(resolve, intervalMs));
    }
    
    throw new Error('Carousel generation timeout');
  }
}

// ===== REACT HOOK ДЛЯ ИСПОЛЬЗОВАНИЯ API =====

import { useState, useCallback } from 'react';

interface UseCarouselGenerationResult {
  isLoading: boolean;
  error: string | null;
  carouselData: CarouselResponse | null;
  generateCarousel: (request: CarouselRequest) => Promise<void>;
  resetState: () => void;
}

export const useCarouselGeneration = (): UseCarouselGenerationResult => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [carouselData, setCarouselData] = useState<CarouselResponse | null>(null);

  const api = new SVGTemplateAPI();

  const generateCarousel = useCallback(async (request: CarouselRequest) => {
    setIsLoading(true);
    setError(null);
    setCarouselData(null);

    try {
      // 1. Создаем карусель
      const { carousel_id } = await api.createAndGenerateCarousel(request);
      
      // 2. Ждем завершения генерации
      const result = await api.waitForCarouselCompletion(carousel_id);
      
      setCarouselData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const resetState = useCallback(() => {
    setIsLoading(false);
    setError(null);
    setCarouselData(null);
  }, []);

  return {
    isLoading,
    error,
    carouselData,
    generateCarousel,
    resetState,
  };
};

// ===== ПРИМЕР ИСПОЛЬЗОВАНИЯ В КОМПОНЕНТЕ =====

export const CarouselGenerator: React.FC = () => {
  const { isLoading, error, carouselData, generateCarousel } = useCarouselGeneration();

  const handleGenerateCarousel = async () => {
    const carouselRequest: CarouselRequest = {
      name: "Property Carousel for 123 Main St",
      slides: [
        {
          templateId: "open-house-main",
          replacements: {
            'dyno.agentName': "John Smith",
            'dyno.propertyAddress': "123 Main Street, City, State 12345",
            'dyno.price': "$450,000",
            'dyno.bedrooms': "3",
            'dyno.bathrooms': "2",
            'dyno.sqft': "1,850",
            'dyno.agentPhone': "(555) 123-4567",
            'dyno.agentEmail': "john@realty.com",
            'dyno.openHouseDate': "Saturday, June 8th",
            'dyno.openHouseTime': "2:00 PM - 4:00 PM"
          },
          imagePath: "https://images.unsplash.com/photo-1560518883-ce09059eeffa"
        },
        {
          templateId: "open-house-photo",
          replacements: {
            'dyno.propertyImage': "https://images.unsplash.com/photo-1560518883-ce09059eeffa"
          },
          imagePath: "https://images.unsplash.com/photo-1560518883-ce09059eeffa"
        },
        {
          templateId: "open-house-photo",
          replacements: {
            'dyno.propertyImage': "https://images.unsplash.com/photo-1570129477492-45c003edd2be"
          },
          imagePath: "https://images.unsplash.com/photo-1570129477492-45c003edd2be"
        }
      ]
    };

    await generateCarousel(carouselRequest);
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Генератор карусели</h2>
      
      <button
        onClick={handleGenerateCarousel}
        disabled={isLoading}
        className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
      >
        {isLoading ? 'Генерируем...' : 'Создать карусель'}
      </button>

      {error && (
        <div className="mt-4 p-4 bg-red-100 text-red-700 rounded">
          Ошибка: {error}
        </div>
      )}

      {carouselData && (
        <div className="mt-6">
          <h3 className="text-xl font-semibold mb-4">Результат:</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {carouselData.slides.map((slide) => (
              <div key={slide.slide_number} className="border rounded p-4">
                <h4 className="font-medium">Слайд {slide.slide_number}</h4>
                <p className="text-sm text-gray-600">Статус: {slide.status}</p>
                {slide.image_url && (
                  <img 
                    src={slide.image_url} 
                    alt={`Slide ${slide.slide_number}`}
                    className="mt-2 w-full h-32 object-cover rounded"
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default CarouselGenerator;

