// 🔗 AGENTFLOW INTEGRATION - TypeScript код для интеграции с API

// ===== ТИПЫ ДАННЫХ =====

interface Template {
  id: string;
  name: string;
  category: string;
  template_role: 'main' | 'photo';
  created_at: string;
  preview_url: string;
  preview_api_url: string;
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
  // Поддержка до 9 дополнительных фото
  'dyno.propertyimage2'?: string;
  'dyno.propertyimage3'?: string;
  'dyno.propertyimage4'?: string;
  'dyno.propertyimage5'?: string;
  'dyno.propertyimage6'?: string;
  'dyno.propertyimage7'?: string;
  'dyno.propertyimage8'?: string;
  'dyno.propertyimage9'?: string;
  'dyno.propertyimage10'?: string;
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
    // Пример данных для полноценной карусели с множественными фото
    const propertyPhotos = [
      "https://images.unsplash.com/photo-1560518883-ce09059eeffa", // Экстерьер
      "https://images.unsplash.com/photo-1570129477492-45c003edd2be", // Гостиная
      "https://images.unsplash.com/photo-1586023492125-27b2c045efd7", // Кухня
      "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2", // Спальня
      "https://images.unsplash.com/photo-1560448075-bb485b067938", // Ванная
      "https://images.unsplash.com/photo-1560448204-61dc36dc98c8", // Столовая
      "https://images.unsplash.com/photo-1560448075-cbc16bb4af8e", // Офис
      "https://images.unsplash.com/photo-1560448204-603b3fc33ddc", // Задний двор
      "https://images.unsplash.com/photo-1560448075-ad2991d8b6e0"  // Гараж
    ];

    const carouselRequest: CarouselRequest = {
      name: "Property Carousel for 123 Main St",
      slides: [
        // Main слайд с основной информацией
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
            'dyno.openHouseTime': "2:00 PM - 4:00 PM",
            'dyno.agentPhoto': "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d"
          },
          imagePath: propertyPhotos[0]
        },
        // Фото слайды (до 9 штук)
        ...propertyPhotos.map((photoUrl, index) => ({
          templateId: "open-house-photo",
          replacements: {
            [`dyno.propertyimage${index + 2}`]: photoUrl
          } as DynoReplacements,
          imagePath: photoUrl
        }))
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

// ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

/**
 * Создает карусель с main слайдом + множественными фото слайдами
 */
export function createPropertyCarousel(
  propertyData: {
    name: string;
    agentName: string;
    propertyAddress: string;
    price: string;
    bedrooms: string;
    bathrooms: string;
    sqft: string;
    agentPhone: string;
    agentEmail: string;
    openHouseDate?: string;
    openHouseTime?: string;
    agentPhoto?: string;
  },
  propertyPhotos: string[], // До 9 фотографий
  mainTemplateId: string = "open-house-main",
  photoTemplateId: string = "open-house-photo"
): CarouselRequest {
  
  // Ограничиваем до 9 фото максимум
  const limitedPhotos = propertyPhotos.slice(0, 9);
  
  const carouselRequest: CarouselRequest = {
    name: `Property Carousel for ${propertyData.propertyAddress}`,
    slides: [
      // Main слайд
      {
        templateId: mainTemplateId,
        replacements: {
          'dyno.agentName': propertyData.agentName,
          'dyno.propertyAddress': propertyData.propertyAddress,
          'dyno.price': propertyData.price,
          'dyno.bedrooms': propertyData.bedrooms,
          'dyno.bathrooms': propertyData.bathrooms,
          'dyno.sqft': propertyData.sqft,
          'dyno.agentPhone': propertyData.agentPhone,
          'dyno.agentEmail': propertyData.agentEmail,
          'dyno.openHouseDate': propertyData.openHouseDate,
          'dyno.openHouseTime': propertyData.openHouseTime,
          'dyno.agentPhoto': propertyData.agentPhoto
        },
        imagePath: limitedPhotos[0] || ""
      },
      // Фото слайды
      ...limitedPhotos.map((photoUrl, index) => ({
        templateId: photoTemplateId,
        replacements: {
          [`dyno.propertyimage${index + 2}`]: photoUrl
        } as DynoReplacements,
        imagePath: photoUrl
      }))
    ]
  };
  
  return carouselRequest;
}

/**
 * Пример использования вспомогательной функции
 */
export const EasyCarouselGenerator: React.FC = () => {
  const { isLoading, error, carouselData, generateCarousel } = useCarouselGeneration();

  const handleGenerateEasyCarousel = async () => {
    // Данные о недвижимости
    const propertyData = {
      name: "Beautiful Family Home",
      agentName: "John Smith",
      propertyAddress: "123 Main Street, Beverly Hills, CA 90210",
      price: "$450,000",
      bedrooms: "3",
      bathrooms: "2",
      sqft: "1,850",
      agentPhone: "(555) 123-4567",
      agentEmail: "john@realty.com",
      openHouseDate: "Saturday, June 8th",
      openHouseTime: "2:00 PM - 4:00 PM",
      agentPhoto: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d"
    };

    // Фотографии недвижимости (до 9 штук)
    const propertyPhotos = [
      "https://images.unsplash.com/photo-1560518883-ce09059eeffa", // Экстерьер
      "https://images.unsplash.com/photo-1570129477492-45c003edd2be", // Гостиная
      "https://images.unsplash.com/photo-1586023492125-27b2c045efd7", // Кухня
      "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2", // Спальня
      "https://images.unsplash.com/photo-1560448075-bb485b067938", // Ванная
    ];

    // Создаем карусель одной функцией
    const carouselRequest = createPropertyCarousel(propertyData, propertyPhotos);
    
    await generateCarousel(carouselRequest);
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Простой генератор карусели</h2>
      
      <button
        onClick={handleGenerateEasyCarousel}
        disabled={isLoading}
        className="bg-green-500 text-white px-4 py-2 rounded disabled:opacity-50"
      >
        {isLoading ? 'Генерируем карусель...' : 'Создать карусель (1 main + 5 фото)'}
      </button>

      {error && (
        <div className="mt-4 p-4 bg-red-100 text-red-700 rounded">
          Ошибка: {error}
        </div>
      )}

      {carouselData && (
        <div className="mt-6">
          <h3 className="text-xl font-semibold mb-4">
            Карусель создана! ({carouselData.slides.length} слайдов)
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {carouselData.slides.map((slide) => (
              <div key={slide.slide_number} className="border rounded p-4">
                <h4 className="font-medium">
                  {slide.slide_number === 1 ? 'Main слайд' : `Фото ${slide.slide_number - 1}`}
                </h4>
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

// ===== КОМПОНЕНТ ДЛЯ ВЫБОРА ШАБЛОНОВ С ПРЕВЬЮ =====

export const TemplateSelector: React.FC<{
  onTemplateSelect: (template: Template) => void;
  selectedTemplate?: Template;
  templateRole?: 'main' | 'photo';
}> = ({ onTemplateSelect, selectedTemplate, templateRole }) => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const api = new SVGTemplateAPI();

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const allTemplates = await api.getTemplates();
      
      // Фильтруем по роли если указана
      const filteredTemplates = templateRole 
        ? allTemplates.filter(t => t.template_role === templateRole)
        : allTemplates;
      
      setTemplates(filteredTemplates);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки шаблонов');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-2">Загружаю шаблоны...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-100 text-red-700 rounded">
        Ошибка: {error}
        <button 
          onClick={loadTemplates}
          className="ml-2 text-red-800 underline"
        >
          Попробовать снова
        </button>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {templates.map((template) => (
        <div
          key={template.id}
          className={`border rounded-lg p-4 cursor-pointer transition-all hover:shadow-lg ${
            selectedTemplate?.id === template.id 
              ? 'border-blue-500 bg-blue-50' 
              : 'border-gray-200 hover:border-gray-300'
          }`}
          onClick={() => onTemplateSelect(template)}
        >
          {/* Превью шаблона */}
          <div className="mb-3 bg-gray-100 rounded overflow-hidden">
            <img
              src={template.preview_url}
              alt={`Превью ${template.name}`}
              className="w-full h-32 object-cover"
              onError={(e) => {
                // Fallback на API URL если прямая ссылка не работает
                const target = e.target as HTMLImageElement;
                if (target.src !== template.preview_api_url) {
                  target.src = template.preview_api_url;
                }
              }}
            />
          </div>
          
          {/* Информация о шаблоне */}
          <h3 className="font-semibold text-sm mb-1">{template.name}</h3>
          <div className="text-xs text-gray-600 space-y-1">
            <div>Категория: {template.category}</div>
            <div>Роль: {template.template_role}</div>
          </div>
          
          {/* Индикатор выбора */}
          {selectedTemplate?.id === template.id && (
            <div className="mt-2 text-blue-600 text-sm font-medium">
              ✓ Выбран
            </div>
          )}
        </div>
      ))}
      
      {templates.length === 0 && (
        <div className="col-span-full text-center py-8 text-gray-500">
          {templateRole 
            ? `Нет шаблонов с ролью "${templateRole}"`
            : 'Нет доступных шаблонов'
          }
        </div>
      )}
    </div>
  );
};

// ===== КОМПОНЕНТ ДЛЯ СОЗДАНИЯ КАРУСЕЛИ С ВЫБОРОМ ШАБЛОНОВ =====

export const CarouselBuilder: React.FC = () => {
  const [mainTemplate, setMainTemplate] = useState<Template | undefined>();
  const [photoTemplate, setPhotoTemplate] = useState<Template | undefined>();
  const [propertyPhotos, setPropertyPhotos] = useState<string[]>(['']);
  const [propertyData, setPropertyData] = useState({
    agentName: '',
    propertyAddress: '',
    price: '',
    bedrooms: '',
    bathrooms: '',
    sqft: '',
    agentPhone: '',
    agentEmail: '',
    agentPhoto: ''
  });

  const { isLoading, error, carouselData, generateCarousel } = useCarouselGeneration();

  const addPhotoField = () => {
    if (propertyPhotos.length < 9) {
      setPropertyPhotos([...propertyPhotos, '']);
    }
  };

  const removePhotoField = (index: number) => {
    setPropertyPhotos(propertyPhotos.filter((_, i) => i !== index));
  };

  const updatePhoto = (index: number, url: string) => {
    const updated = [...propertyPhotos];
    updated[index] = url;
    setPropertyPhotos(updated);
  };

  const handleGenerateCarousel = async () => {
    if (!mainTemplate || !photoTemplate) {
      alert('Выберите оба шаблона (Main и Photo)');
      return;
    }

    const validPhotos = propertyPhotos.filter(photo => photo.trim() !== '');
    
    if (validPhotos.length === 0) {
      alert('Добавьте хотя бы одну фотографию');
      return;
    }

    const carouselRequest = createPropertyCarousel(
      propertyData,
      validPhotos,
      mainTemplate.id,
      photoTemplate.id
    );

    await generateCarousel(carouselRequest);
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-8">
      <h1 className="text-3xl font-bold">Создание карусели недвижимости</h1>
      
      {/* Выбор Main шаблона */}
      <div>
        <h2 className="text-xl font-semibold mb-4">1. Выберите Main шаблон</h2>
        <TemplateSelector
          templateRole="main"
          selectedTemplate={mainTemplate}
          onTemplateSelect={setMainTemplate}
        />
      </div>

      {/* Выбор Photo шаблона */}
      <div>
        <h2 className="text-xl font-semibold mb-4">2. Выберите Photo шаблон</h2>
        <TemplateSelector
          templateRole="photo"
          selectedTemplate={photoTemplate}
          onTemplateSelect={setPhotoTemplate}
        />
      </div>

      {/* Данные о недвижимости */}
      <div>
        <h2 className="text-xl font-semibold mb-4">3. Заполните данные</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            type="text"
            placeholder="Имя агента"
            value={propertyData.agentName}
            onChange={(e) => setPropertyData({...propertyData, agentName: e.target.value})}
            className="border rounded px-3 py-2"
          />
          <input
            type="text"
            placeholder="Адрес недвижимости"
            value={propertyData.propertyAddress}
            onChange={(e) => setPropertyData({...propertyData, propertyAddress: e.target.value})}
            className="border rounded px-3 py-2"
          />
          <input
            type="text"
            placeholder="Цена"
            value={propertyData.price}
            onChange={(e) => setPropertyData({...propertyData, price: e.target.value})}
            className="border rounded px-3 py-2"
          />
          <input
            type="text"
            placeholder="Спальни"
            value={propertyData.bedrooms}
            onChange={(e) => setPropertyData({...propertyData, bedrooms: e.target.value})}
            className="border rounded px-3 py-2"
          />
          <input
            type="text"
            placeholder="Ванные"
            value={propertyData.bathrooms}
            onChange={(e) => setPropertyData({...propertyData, bathrooms: e.target.value})}
            className="border rounded px-3 py-2"
          />
          <input
            type="text"
            placeholder="Площадь (кв.фт)"
            value={propertyData.sqft}
            onChange={(e) => setPropertyData({...propertyData, sqft: e.target.value})}
            className="border rounded px-3 py-2"
          />
          <input
            type="text"
            placeholder="Телефон агента"
            value={propertyData.agentPhone}
            onChange={(e) => setPropertyData({...propertyData, agentPhone: e.target.value})}
            className="border rounded px-3 py-2"
          />
          <input
            type="text"
            placeholder="Email агента"
            value={propertyData.agentEmail}
            onChange={(e) => setPropertyData({...propertyData, agentEmail: e.target.value})}
            className="border rounded px-3 py-2"
          />
          <input
            type="url"
            placeholder="Фото агента (URL)"
            value={propertyData.agentPhoto}
            onChange={(e) => setPropertyData({...propertyData, agentPhoto: e.target.value})}
            className="border rounded px-3 py-2"
          />
        </div>
      </div>

      {/* Фотографии недвижимости */}
      <div>
        <h2 className="text-xl font-semibold mb-4">4. Добавьте фотографии (до 9 штук)</h2>
        <div className="space-y-2">
          {propertyPhotos.map((photo, index) => (
            <div key={index} className="flex gap-2">
              <input
                type="url"
                placeholder={`URL фотографии ${index + 1}`}
                value={photo}
                onChange={(e) => updatePhoto(index, e.target.value)}
                className="flex-1 border rounded px-3 py-2"
              />
              {propertyPhotos.length > 1 && (
                <button
                  onClick={() => removePhotoField(index)}
                  className="px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                >
                  Удалить
                </button>
              )}
            </div>
          ))}
          
          {propertyPhotos.length < 9 && (
            <button
              onClick={addPhotoField}
              className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              + Добавить фото
            </button>
          )}
        </div>
      </div>

      {/* Генерация */}
      <div>
        <button
          onClick={handleGenerateCarousel}
          disabled={isLoading || !mainTemplate || !photoTemplate}
          className="w-full py-3 bg-blue-500 text-white rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-600"
        >
          {isLoading ? 'Генерирую карусель...' : 'Создать карусель'}
        </button>
      </div>

      {/* Ошибка */}
      {error && (
        <div className="p-4 bg-red-100 text-red-700 rounded">
          Ошибка: {error}
        </div>
      )}

      {/* Результат */}
      {carouselData && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Карусель создана!</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {carouselData.slides.map((slide) => (
              <div key={slide.slide_number} className="border rounded p-4">
                <h3 className="font-medium mb-2">
                  {slide.slide_number === 1 ? 'Main слайд' : `Фото ${slide.slide_number - 1}`}
                </h3>
                {slide.image_url && (
                  <img 
                    src={slide.image_url} 
                    alt={`Slide ${slide.slide_number}`}
                    className="w-full h-32 object-cover rounded"
                  />
                )}
                <p className="text-sm text-gray-600 mt-2">Статус: {slide.status}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default CarouselGenerator;

