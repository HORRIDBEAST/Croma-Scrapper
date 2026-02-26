<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 font-sans">

    <!-- Header -->
    <header class="bg-white/5 backdrop-blur-md border-b border-white/10 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/>
              </svg>
            </div>
            <div>
              <h1 class="text-xl font-bold text-white">Pharma Intelligence</h1>
              <p class="text-xs text-blue-300">ZS Associates — Real-time Industry Feed</p>
            </div>
          </div>

          <div class="flex items-center space-x-3">
            <span v-if="lastUpdated" class="text-xs text-slate-400 hidden md:block">
              Last updated: {{ lastUpdated }}
            </span>
            <button
              @click="triggerRefresh"
              :disabled="refreshing"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-sm font-semibold transition-all duration-200 flex items-center gap-2 disabled:opacity-50"
            >
              <svg :class="{'animate-spin': refreshing}" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
              </svg>
              {{ refreshing ? 'Refreshing...' : 'Refresh' }}
            </button>
            <router-link to="/" class="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl text-sm font-medium transition-all duration-200">
              ← Croma
            </router-link>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

      <!-- Stats Bar -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div v-for="stat in stats" :key="stat.label"
          class="bg-white/5 border border-white/10 rounded-2xl p-4 text-center">
          <div class="text-2xl font-bold text-white">{{ stat.value }}</div>
          <div class="text-xs text-slate-400 mt-1">{{ stat.label }}</div>
        </div>
      </div>

      <!-- Search Bar -->
      <div class="mb-6">
        <div class="relative">
          <svg class="w-5 h-5 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search drug names, companies, announcements..."
            class="w-full bg-white/10 border border-white/20 text-white placeholder-slate-400 rounded-2xl pl-12 pr-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
          />
        </div>
      </div>

      <!-- Company Filter -->
      <div class="mb-4">
        <p class="text-xs text-slate-400 uppercase tracking-widest mb-3">Filter by Company</p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="company in ['All', ...companies]"
            :key="company"
            @click="selectedCompany = company"
            :style="selectedCompany === company && company !== 'All' ? { backgroundColor: getCompanyColor(company), borderColor: getCompanyColor(company) } : {}"
            :class="[
              'px-3 py-1.5 rounded-full text-xs font-semibold border transition-all duration-200',
              selectedCompany === company
                ? (company === 'All' ? 'bg-blue-600 border-blue-600 text-white' : 'text-white')
                : 'bg-white/5 border-white/20 text-slate-300 hover:bg-white/10'
            ]"
          >
            {{ company }}
          </button>
        </div>
      </div>

      <!-- Category Filter -->
      <div class="mb-8">
        <p class="text-xs text-slate-400 uppercase tracking-widest mb-3">Filter by Category</p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="cat in ['All', 'Drug Launch', 'Innovation', 'Events', 'Acquisition', 'Earnings', 'General']"
            :key="cat"
            @click="selectedCategory = cat"
            :class="[
              'px-3 py-1.5 rounded-full text-xs font-semibold border transition-all duration-200',
              selectedCategory === cat
                ? 'bg-cyan-600 border-cyan-600 text-white'
                : 'bg-white/5 border-white/20 text-slate-300 hover:bg-white/10'
            ]"
          >
            {{ cat === 'All' ? 'All Categories' : cat }}
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-20">
        <div class="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p class="mt-4 text-slate-400">Loading pharma intelligence...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="text-center py-16 bg-red-500/10 border border-red-500/20 rounded-2xl p-8">
        <p class="text-red-400 font-semibold">{{ error }}</p>
        <button @click="fetchNews" class="mt-4 px-6 py-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition-all">Retry</button>
      </div>

      <!-- Empty -->
      <div v-else-if="news.length === 0" class="text-center py-20">
        <svg class="w-16 h-16 text-slate-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        <p class="text-slate-400">No articles found. Try adjusting your filters.</p>
        <p class="text-slate-500 text-sm mt-2">Make sure you've run <code class="text-cyan-400">pharma_scraper.py</code> first.</p>
      </div>

      <!-- News Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        <div
          v-for="article in news"
          :key="article.id"
          class="group bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 rounded-2xl overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl flex flex-col"
        >
          <!-- Company Tag -->
          <div class="flex items-center justify-between px-5 pt-5 pb-3">
            <span
              class="px-3 py-1 rounded-full text-xs font-bold text-white"
              :style="{ backgroundColor: article.company_color + '33', color: article.company_color, border: '1px solid ' + article.company_color + '55' }"
            >
              {{ article.company }}
            </span>
            <span :class="categoryBadgeClass(article.category)" class="px-3 py-1 rounded-full text-xs font-semibold">
              {{ article.category }}
            </span>
          </div>

          <!-- Content -->
          <div class="px-5 pb-4 flex-grow">
            <h3 class="text-white font-semibold text-sm leading-snug mb-2 group-hover:text-blue-300 transition-colors line-clamp-3">
              {{ article.title }}
            </h3>
            <p class="text-slate-400 text-xs leading-relaxed line-clamp-3">
              {{ article.summary || 'No summary available.' }}
            </p>
          </div>

          <!-- Footer -->
          <div class="px-5 pb-5 flex items-center justify-between mt-auto border-t border-white/5 pt-3">
            <div>
              <p class="text-slate-500 text-xs">{{ article.source }}</p>
              <p class="text-slate-600 text-xs">{{ article.published }}</p>
            </div>
            <a
              :href="article.link"
              target="_blank"
              rel="noopener noreferrer"
              class="px-3 py-1.5 bg-blue-600/80 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg transition-all duration-200 flex items-center gap-1"
            >
              Read
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
              </svg>
            </a>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="text-center py-8 mt-8 border-t border-white/10">
      <p class="text-slate-500 text-sm">ZS Associates • Pharma Intelligence Feed • Powered by Google News RSS</p>
    </footer>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

const COMPANY_COLORS = {
  "Pfizer": "#0093D0", "Novartis": "#EC0016", "Sanofi": "#7B2D8B",
  "Takeda": "#E4002B", "Merck": "#009B77", "Bayer": "#10A0E3",
  "AbbVie": "#071D49", "Bristol Myers Squibb": "#003865",
  "Johnson & Johnson": "#CC0000", "Roche": "#0066CC",
  "Eli Lilly": "#D52B1E", "AstraZeneca": "#830051", "Amgen": "#002A5C"
}

export default {
  name: 'PharmaApp',
  setup() {
    const news = ref([])
    const companies = ref([])
    const loading = ref(true)
    const error = ref(null)
    const searchQuery = ref('')
    const selectedCompany = ref('All')
    const selectedCategory = ref('All')
    const lastUpdated = ref('')
    const refreshing = ref(false)
    const totalCount = ref(0)

    const stats = computed(() => [
      { label: 'Total Articles', value: totalCount.value },
      { label: 'Companies Tracked', value: 13 },
      { label: 'Showing Now', value: news.value.length },
      { label: 'Categories', value: 6 }
    ])

    const getCompanyColor = (company) => COMPANY_COLORS[company] || '#3B82F6'

    const categoryBadgeClass = (cat) => {
      const map = {
        'Drug Launch': 'bg-green-500/20 text-green-400',
        'Innovation': 'bg-purple-500/20 text-purple-400',
        'Events': 'bg-yellow-500/20 text-yellow-400',
        'Acquisition': 'bg-orange-500/20 text-orange-400',
        'Earnings': 'bg-blue-500/20 text-blue-400',
        'General': 'bg-slate-500/20 text-slate-400',
      }
      return map[cat] || 'bg-slate-500/20 text-slate-400'
    }

    const fetchNews = async () => {
      loading.value = true
      error.value = null
      try {
        const params = new URLSearchParams()
        if (selectedCompany.value !== 'All') params.append('company', selectedCompany.value)
        if (selectedCategory.value !== 'All') params.append('category', selectedCategory.value)
        if (searchQuery.value) params.append('search', searchQuery.value)

        const res = await fetch(`/pharma-api/news?${params.toString()}`)
        if (!res.ok) {
          const err = await res.json()
          throw new Error(err.message || `HTTP ${res.status}`)
        }
        const data = await res.json()
        news.value = data.news || []
        totalCount.value = data.count || 0
        lastUpdated.value = data.last_updated || ''
      } catch (err) {
        console.error(err)
        error.value = `Failed to load news: ${err.message}`
      } finally {
        loading.value = false
      }
    }

    const fetchCompanies = async () => {
      try {
        const res = await fetch('/pharma-api/companies')
        companies.value = await res.json()
      } catch (e) {
        console.error('Could not load companies', e)
      }
    }

    const triggerRefresh = async () => {
      refreshing.value = true
      try {
        await fetch('/pharma-api/refresh', { method: 'POST' })
        setTimeout(() => {
          fetchNews()
          refreshing.value = false
        }, 35000) // wait 35s for scraper to finish
      } catch (e) {
        refreshing.value = false
      }
    }

    // Watchers for filter changes
    const applyFilters = () => fetchNews()

    onMounted(async () => {
      await fetchCompanies()
      await fetchNews()
    })

    return {
      news, companies, loading, error, searchQuery,
      selectedCompany, selectedCategory, lastUpdated,
      refreshing, stats, getCompanyColor, categoryBadgeClass,
      fetchNews, triggerRefresh, applyFilters
    }
  },
  watch: {
    selectedCompany() { this.fetchNews() },
    selectedCategory() { this.fetchNews() },
    searchQuery(val) {
      clearTimeout(this._searchTimer)
      this._searchTimer = setTimeout(() => this.fetchNews(), 400)
    }
  }
}
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>