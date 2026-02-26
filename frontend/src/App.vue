<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 font-sans">
    <!-- Header -->
    <header class="bg-white/80 backdrop-blur-md border-b border-slate-200/60 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gradient-to-r from-red-500 to-red-600 rounded-xl flex items-center justify-center shadow-md shadow-red-500/20">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <rect width="20" height="15" x="2" y="3" rx="2" ry="2"/>
                <line x1="8" x2="16" y1="21" y2="21"/>
                <line x1="12" x2="12" y1="17" y2="21"/>
              </svg>
            </div>
            <div>
              <h1 class="text-xl font-bold bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
                Croma
              </h1>
              <p class="text-xs text-slate-500">Televisions & Accessories</p>
            </div>
          </div>
          
          <div class="flex items-center space-x-2 md:space-x-4">
            <div class="relative flex items-center bg-white/70 backdrop-blur-md rounded-2xl shadow-lg border border-slate-200 px-2 py-1 transition-all duration-300 focus-within:ring-2 focus-within:ring-red-400/30">
              <span class="flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-tr from-red-500 to-red-600 shadow-md mr-2">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <circle cx="11" cy="11" r="8"/>
                  <path d="m21 21-4.35-4.35"/>
                </svg>
              </span>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search products..."
                class="flex-1 bg-transparent outline-none border-none text-base px-2 py-2 transition-all duration-200 focus:placeholder:text-slate-400"
              />
              <button
                @click="fetchPageElements"
                class="ml-2 px-5 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl text-sm font-semibold shadow-md hover:from-blue-600 hover:to-blue-700 transition-all duration-200 transform hover:scale-105"
              >
                Search
              </button>
            </div>

            <div class="flex items-center space-x-4">
              <button class="relative">
                <svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                </svg>
                <span v-if="loveCount" class="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full px-1.5">{{ loveCount }}</span>
              </button>
              <button class="relative">
                <svg class="w-6 h-6 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <circle cx="9" cy="21" r="1"/>
                  <circle cx="20" cy="21" r="1"/>
                  <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
                </svg>
                <span v-if="cartCount" class="absolute -top-2 -right-2 bg-blue-500 text-white text-xs rounded-full px-1.5">{{ cartCount }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Hero Section -->
      <div class="mb-12 text-center">
        <h2 class="text-4xl md:text-5xl font-bold bg-gradient-to-r from-slate-800 via-slate-700 to-slate-600 bg-clip-text text-transparent mb-4">
          Premium Electronics Collection
        </h2>
        <p class="text-lg text-slate-600 max-w-2xl mx-auto">
          Discover our curated selection of cutting-edge televisions and premium accessories
        </p>
      </div>

      <!-- Filters & Sorting -->
      <div class="mb-8 flex flex-col md:flex-row justify-between items-center gap-4">
        <div class="flex flex-wrap gap-2 justify-center">
          <button
            v-for="category in categories"
            :key="category"
            @click="selectedCategory = category"
            :class="[
              'px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 transform hover:scale-105',
              selectedCategory === category
                ? 'bg-gradient-to-r from-red-500 to-red-600 text-white shadow-lg shadow-red-500/25'
                : 'bg-white text-slate-600 border border-slate-200 hover:border-red-300 hover:text-red-600'
            ]"
          >
            {{ category }}
          </button>
        </div>
        <div class="relative">
          <select v-model="sortBy" class="appearance-none bg-white border border-slate-200 rounded-full px-4 py-2 pr-8 text-sm font-medium text-slate-600 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-400">
            <option value="default">Sort by: Default</option>
            <option value="price-asc">Price: Low to High</option>
            <option value="price-desc">Price: High to Low</option>
            <option value="name-asc">Name: A to Z</option>
          </select>
          <svg class="w-4 h-4 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path d="m6 9 6 6 6-6"/>
          </svg>
        </div>
      </div>

      <!-- Debug Info -->
      

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-16">
        <div class="w-12 h-12 border-4 border-red-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p class="mt-4 text-slate-600">Loading premium electronics...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-16 bg-red-50 p-8 rounded-2xl border border-red-100">
        <svg class="w-12 h-12 text-red-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
          <path d="M12 9v4"/>
          <path d="m12 17 .01 0"/>
        </svg>
        <p class="mt-4 text-red-700 font-semibold">Oops! Something went wrong.</p>
        <p class="text-red-600 mb-4">{{ error }}</p>
        <button @click="fetchProducts" class="px-6 py-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition-all duration-200 transform hover:scale-105">
          Retry
        </button>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredProducts.length === 0 && !loading" class="text-center py-16">
        <svg class="w-16 h-16 text-slate-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <rect width="20" height="15" x="2" y="3" rx="2" ry="2"/>
          <line x1="8" x2="16" y1="21" y2="21"/>
          <line x1="12" x2="12" y1="17" y2="21"/>
        </svg>
        <p class="text-slate-500 text-lg">No products found</p>
        <p class="text-slate-400">Try adjusting your search or filters</p>
      </div>

      <!-- Product Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-3  gap-8">
        <div
          v-for="product in filteredProducts"
          :key="product.id || product.title"
          class="group bg-white rounded-2xl shadow-sm hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-3 border border-slate-100"
        >
          <!-- Product Image -->
          <div class="relative overflow-hidden bg-gradient-to-br from-slate-50 to-slate-100 aspect-square">
            <img
              v-if="product.image_url"
              :src="product.image_url"
              :alt="product.title"
              class="w-full h-full object-contain p-4 group-hover:scale-110 transition-transform duration-700"
              @error="handleImageError"
            />
            <div v-else class="w-full h-full flex items-center justify-center">
              <svg class="w-16 h-16 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <rect width="20" height="15" x="2" y="3" rx="2" ry="2"/>
                <line x1="8" x2="16" y1="21" y2="21"/>
                <line x1="12" x2="12" y1="17" y2="21"/>
              </svg>
            </div>
            
            <!-- Wishlist Button -->
            <div class="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              <button class="p-2 bg-white/90 backdrop-blur-sm rounded-full shadow-lg hover:bg-white transition-all duration-200 hover:scale-110">
                <svg class="w-4 h-4 text-slate-600 hover:text-red-500 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                </svg>
              </button>
            </div>
            
            <!-- Discount Badge -->
            <div v-if="product.discount && product.discount > 0" class="absolute top-4 left-4">
              <span class="px-3 py-1 bg-gradient-to-r from-red-500 to-red-600 text-white text-xs font-semibold rounded-full shadow-lg">
                {{ product.discount }}% OFF
              </span>
            </div>
          </div>

          <!-- Product Info -->
          <div class="p-6 flex flex-col">
            <div class="mb-4 flex-grow">
              <p class="text-slate-500 text-xs mb-2 uppercase tracking-wide">{{ product.brand }}</p>
              <h3 class="font-semibold text-slate-800 text-base mb-3 leading-6 group-hover:text-red-600 transition-colors duration-200">
                {{ product.title }}
              </h3>
            </div>

            <!-- Price Section -->
            <div class="mb-6">
              <div class="flex items-baseline gap-2 mb-2">
                <span class="text-2xl font-bold text-slate-900">{{ product.sale_price || 'N/A' }}</span>
                <span v-if="product.price && product.price !== product.sale_price" class="text-sm text-slate-400 line-through">
                  {{ product.price }}
                </span>
              </div>
              <div v-if="product.discount && product.discount > 0" class="text-sm text-green-600 font-medium">
                You save {{ product.savings || 'N/A' }}
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="space-y-2">
              <button
                class="w-full bg-gradient-to-r from-red-500 to-red-600 text-white py-3 rounded-xl font-semibold hover:from-red-600 hover:to-red-700 transition-all duration-200 transform hover:scale-105 shadow-lg shadow-red-500/25"
                @click="addToCart(product)"
              >
                Add to Cart
              </button>
              <button
                class="w-full bg-slate-100 text-slate-700 py-2 rounded-xl font-medium hover:bg-slate-200 transition-all duration-200 flex items-center justify-center gap-2"
                @click="toggleLove(product)"
              >
                <svg :class="{'text-red-500': lovedItems.includes(product.id), 'text-slate-400': !lovedItems.includes(product.id)}" class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41 0.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
    </svg>
                {{ lovedItems.includes(product.id) ? 'Loved' : 'Love' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="bg-slate-900 text-white py-12 mt-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <div class="flex items-center justify-center space-x-2 mb-4">
            <div class="w-8 h-8 bg-gradient-to-r from-red-500 to-red-600 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <rect width="20" height="15" x="2" y="3" rx="2" ry="2"/>
                <line x1="8" x2="16" y1="21" y2="21"/>
                <line x1="12" x2="12" y1="17" y2="21"/>
              </svg>
            </div>
            <span class="text-xl font-bold">Croma</span>
          </div>
          <p class="text-slate-400">Premium Electronics • Scraped with Excellence</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'CromaElectronicsStore',
  setup() {
    // Reactive state
    const products = ref([])
    const loading = ref(true)
    const error = ref(null)
    const searchQuery = ref('')
    const selectedCategory = ref('All')
    const sortBy = ref('default')
    const cartCount = ref(0)
    const loveCount = ref(0)
    const cartItems = ref([])
    const lovedItems = ref([])

    // Utility functions
    const parsePrice = (priceStr) => {
      if (!priceStr) return 0
      const numericValue = Number(priceStr.replace(/[^0-9.-]+/g, ''))
      return isNaN(numericValue) ? 0 : numericValue
    }

    const extractBrand = (title) => {
      if (!title) return 'Electronics'
      const brands = ['SAMSUNG', 'LG', 'SONY', 'TCL', 'XIAOMI', 'AMAZON', 'CROMA', 'KODAK', 'WESTINGHOUSE', 'PHILIPS', 'BOSE', 'JBL', 'APPLE', 'HISENSE', 'PANASONIC']
      const upperTitle = title.toUpperCase()
      for (const brand of brands) {
        if (upperTitle.includes(brand)) {
          return brand.charAt(0) + brand.slice(1).toLowerCase()
        }
      }
      return 'Electronics'
    }

    const guessCategory = (title) => {
      if (!title) return 'Accessories'
      const upperTitle = title.toUpperCase()
      if (upperTitle.includes('TV') || upperTitle.includes('TELEVISION')) return 'Televisions'
      if (upperTitle.includes('SOUNDBAR') || upperTitle.includes('SPEAKER') || upperTitle.includes('AUDIO')) return 'Audio'
      if (upperTitle.includes('STREAMING') || upperTitle.includes('STICK') || upperTitle.includes('REMOTE')) return 'Streaming'
      if (upperTitle.includes('SMART') || upperTitle.includes('HUE') || upperTitle.includes('LIGHT')) return 'Smart Home'
      return 'Accessories'
    }

    // Computed properties
    const processedProducts = computed(() => {
      return products.value.map(product => {
        const salePrice = parsePrice(product.sale_price)
        const originalPrice = parsePrice(product.price)
        const discount = originalPrice > salePrice ? Math.round(((originalPrice - salePrice) / originalPrice) * 100) : 0
        const savings = originalPrice > salePrice ? `₹${(originalPrice - salePrice).toLocaleString()}` : ''
        
        return {
          ...product,
          id: product.sku || product.title || Math.random(),
          numericSalePrice: salePrice,
          numericOriginalPrice: originalPrice,
          discount: discount,
          savings: savings,
          brand: extractBrand(product.title),
          category: guessCategory(product.title)
        }
      })
    })

    const categories = computed(() => {
      const cats = processedProducts.value.map(p => p.category)
      return ['All', ...new Set(cats)]
    })

    const filteredProducts = computed(() => {
      let filtered = [...processedProducts.value]
      
      // Category filter
      if (selectedCategory.value !== 'All') {
        filtered = filtered.filter(product => product.category === selectedCategory.value)
      }
      
      // Search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(product =>
          (product.title && product.title.toLowerCase().includes(query)) ||
          (product.brand && product.brand.toLowerCase().includes(query))
        )
      }
      
      // Sort
      switch (sortBy.value) {
        case 'price-asc':
          filtered.sort((a, b) => a.numericSalePrice - b.numericSalePrice)
          break
        case 'price-desc':
          filtered.sort((a, b) => b.numericSalePrice - a.numericSalePrice)
          break
        case 'name-asc':
          filtered.sort((a, b) => (a.title || '').localeCompare(b.title || ''))
          break
      }
      
      return filtered
    })

    // Methods
    const fetchProducts = async () => {
      loading.value = true
      error.value = null
      try {
        const response = await fetch('/api/products')
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.message || `HTTP error! Status: ${response.status}`)
        }
        const data = await response.json()
        products.value = Array.isArray(data) ? data : []
        console.log('Fetched products:', products.value)
      } catch (err) {
        console.error('Error fetching products:', err)
        error.value = `Failed to load products. ${err.message}`
      } finally {
        loading.value = false
      }
    }

    const fetchPageElements = async () => {
      try {
        const response = await fetch('/api/scraped-content')
        const result = await response.json()
        if (result.success) {
          console.log('Successfully fetched page elements:', result.data)
          alert('Head and Header content fetched successfully! Check the browser console (F12).')
        } else {
          throw new Error(result.message || 'Failed to fetch page elements')
        }
      } catch (err) {
        console.error('Error fetching page elements:', err)
        alert(`Failed to fetch page elements: ${err.message}`)
      }
    }

    const handleImageError = (event) => {
      event.target.style.display = 'none'
    }

    const addToCart = (product) => {
      if (!cartItems.value.includes(product.id)) {
        cartItems.value.push(product.id)
        cartCount.value++
      }
    }

    const toggleLove = (product) => {
      const idx = lovedItems.value.indexOf(product.id)
      if (idx === -1) {
        lovedItems.value.push(product.id)
        loveCount.value++
      } else {
        lovedItems.value.splice(idx, 1)
        loveCount.value--
      }
    }

    // Lifecycle
    onMounted(() => {
      fetchProducts()
    })

    return {
      products,
      loading,
      error,
      searchQuery,
      selectedCategory,
      sortBy,
      processedProducts,
      categories,
      filteredProducts,
      fetchProducts,
      fetchPageElements,
      handleImageError,
      cartCount,
      loveCount,
      cartItems,
      lovedItems,
      addToCart,
      toggleLove
    }
  }
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Custom scrollbar for webkit browsers */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>