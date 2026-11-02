<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { 
    Camera, 
    Upload, 
    FileText, 
    RefreshCw, 
    CheckCircle2, 
    AlertTriangle, 
    AlertOctagon, 
    ShieldCheck, 
    Printer, 
    RotateCcw,
    ArrowRight,
    Sparkles,
    Activity,
    Info,
    Check,
    HeartPulse,
    Droplet,
    Flame,
    Smartphone,
    Monitor,
    ExternalLink,
    Zap,
    ChevronDown
  } from 'lucide-svelte';

  interface AllergenInfo {
    bahan: string;
    kategori_alergen: string;
    status_bahaya: string;
    kutipan_pasal: string;
  }

  interface GGLNutrisi {
    takaran_saji_gram: number | null;
    gula_gram: number | null;
    natrium_mg: number | null;
    lemak_total_gram: number | null;
    persen_gula_harian: number | null;
    persen_natrium_harian: number | null;
    persen_lemak_harian: number | null;
    status_gula: string;
    status_natrium: string;
    status_lemak: string;
  }

  interface PemanisBuatanInfo {
    terdeteksi: boolean;
    jenis_pemanis: string[];
    peringatan_wajib: string | null;
  }

  interface ScanResponse {
    nama_produk: string;
    status_keamanan_umum: string;
    ringkasan_eksekutif: string;
    alergen_terdeteksi: AllergenInfo[];
    analisis_ggl: GGLNutrisi;
    pemanis_buatan: PemanisBuatanInfo;
    rekomendasi_konsumen: string;
  }

  // Device view mode: 'mobile' (Phone Frame) or 'desktop' (Full width)
  // Default to 'mobile' as requested for instant phone preview inside Antigravity!
  let viewMode: 'mobile' | 'desktop' = 'mobile';

  // Active Tab for input: DEFAULT TO 'upload' so camera NEVER turns on automatically!
  let activeTab: 'upload' | 'camera' | 'text' = 'upload';
  
  // Camera WebRTC state
  let videoElement: HTMLVideoElement | null = null;
  let mediaStream: MediaStream | null = null;
  let cameraActive = false;
  let cameraError: string | null = null;
  let facingMode: 'environment' | 'user' = 'environment';
  let isCapturing = false;

  // Selected file & text input
  let selectedFile: File | null = null;
  let previewUrl: string | null = null;
  let textInput = '';

  // Consumer risk profile: 10 BPOM Allergens & 3 Metabolic Focuses
  let userAllergies: string[] = [];
  let focusDiabetes = false;
  let focusHipertensi = false;
  let focusLemak = false;

  // Audit results & loading state
  let loading = false;
  let errorMsg: string | null = null;
  let result: ScanResponse | null = null;

  // 10 Kategori Alergen Resmi BPOM (Peraturan BPOM No. 31 Tahun 2018 Pasal 41)
  const allergenOptions = [
    { id: 'Susu', label: 'Susu & Laktosa', sub: 'Kasein, whey, keju, mentega', icon: '🥛' },
    { id: 'Gluten', label: 'Gluten & Serealia', sub: 'Gandum, terigu, oat, barley', icon: '🌾' },
    { id: 'Kedelai', label: 'Kedelai & Soya', sub: 'Lesitin kedelai, tahu, tempe', icon: '🫘' },
    { id: 'Kacang', label: 'Kacang Tanah', sub: 'Peanut, selai kacang', icon: '🥜' },
    { id: 'Kacang Pohon', label: 'Kacang Pohon (Tree Nuts)', sub: 'Almond, mede, walnut, hazelnut', icon: '🌰' },
    { id: 'Telur', label: 'Telur & Olahannya', sub: 'Albumin, kuning & putih telur', icon: '🥚' },
    { id: 'Ikan', label: 'Ikan & Olahannya', sub: 'Gelatin ikan, minyak ikan', icon: '🐟' },
    { id: 'Krustasea', label: 'Krustasea', sub: 'Udang, kepiting, lobster, ebi', icon: '🦐' },
    { id: 'Moluska', label: 'Moluska', sub: 'Cumi, kerang, tiram, gurita', icon: '🦑' },
    { id: 'Sulfit', label: 'Sulfit / Sulfite', sub: 'Belerang dioksida ≥ 10 mg/kg', icon: '🧪' }
  ];

  onDestroy(() => {
    stopCamera();
  });

  async function startCamera() {
    cameraError = null;
    stopCamera();

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Akses kamera langsung tidak didukung pada konteks ini. Gunakan tab Unggah Galeri/File.');
      }

      const constraints: MediaStreamConstraints = {
        video: {
          facingMode: facingMode,
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      };

      mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      cameraActive = true;

      setTimeout(() => {
        if (videoElement && mediaStream) {
          videoElement.srcObject = mediaStream;
          videoElement.play().catch(e => console.warn('Video err:', e));
        }
      }, 100);

    } catch (err: any) {
      console.error('Camera error:', err);
      cameraActive = false;
      cameraError = err.message || 'Izin kamera belum aktif. Berikan izin akses kamera pada peramban Anda.';
    }
  }

  function stopCamera() {
    if (mediaStream) {
      mediaStream.getTracks().forEach(t => t.stop());
      mediaStream = null;
    }
    cameraActive = false;
  }

  function switchCamera() {
    facingMode = facingMode === 'environment' ? 'user' : 'environment';
    startCamera();
  }

  function capturePhoto() {
    if (!videoElement) return;

    isCapturing = true;
    const canvas = document.createElement('canvas');
    canvas.width = videoElement.videoWidth || 1280;
    canvas.height = videoElement.videoHeight || 720;

    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
      canvas.toBlob((blob) => {
        if (blob) {
          selectedFile = new File([blob], `label-${Date.now()}.jpg`, { type: 'image/jpeg' });
          previewUrl = URL.createObjectURL(blob);
          stopCamera();
        }
        isCapturing = false;
      }, 'image/jpeg', 0.92);
    } else {
      isCapturing = false;
    }
  }

  function retakePhoto() {
    selectedFile = null;
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      previewUrl = null;
    }
    startCamera();
  }

  function setTab(tab: 'upload' | 'camera' | 'text') {
    activeTab = tab;
    errorMsg = null;
    if (tab === 'camera') {
      if (!previewUrl) startCamera();
    } else {
      stopCamera();
    }
  }

  function handleFileSelect(e: Event) {
    const target = e.target as HTMLInputElement;
    if (target.files && target.files[0]) {
      setUploadedFile(target.files[0]);
    }
  }

  function setUploadedFile(file: File) {
    if (!file.type.startsWith('image/')) {
      errorMsg = 'Format file tidak didukung. Harap pilih gambar JPG, PNG, atau WEBP.';
      return;
    }
    selectedFile = file;
    errorMsg = null;
    const reader = new FileReader();
    reader.onload = (e) => {
      previewUrl = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }

  let customAllergyInput = '';

  function addCustomAllergy() {
    const trimmed = customAllergyInput.trim();
    if (!trimmed) return;
    if (!userAllergies.includes(trimmed)) {
      userAllergies = [...userAllergies, trimmed];
    }
    customAllergyInput = '';
  }

  function removeAllergy(id: string) {
    userAllergies = userAllergies.filter(a => a !== id);
  }

  function toggleAllergy(id: string) {
    if (userAllergies.includes(id)) {
      userAllergies = userAllergies.filter(a => a !== id);
    } else {
      userAllergies = [...userAllergies, id];
    }
  }

  function loadSample(type: 'biscuit' | 'soda' | 'diet') {
    setTab('text');
    if (type === 'biscuit') {
      textInput = "INFORMASI NILAI GIZI:\nTakaran saji: 30g (3 keping)\nLemak total: 6g\nGula: 12g\nNatrium: 130mg\n\nKOMPOSISI:\nTepung terigu, gula pasir, minyak nabati, kakao bubuk, krimer nabati (mengandung kasein), susu bubuk skim (3%), pengemulsi lesitin kedelai, perisa vanila.";
    } else if (type === 'soda') {
      textInput = "INFORMASI NILAI GIZI:\nTakaran saji: 250ml\nEnergi total: 140 kkal\nLemak total: 0g\nGula: 33g\nNatrium: 45mg\n\nKOMPOSISI:\nAir berkarbonasi, sirup fruktosa jagung, pewarna karamel IV, asam fosfat, kafein, perisa alami.";
    } else if (type === 'diet') {
      textInput = "INFORMASI NILAI GIZI:\nTakaran saji: 15ml\nEnergi total: 5 kkal\nGula: 0g\nLemak: 0g\nNatrium: 15mg\n\nKOMPOSISI:\nAir, pengatur keasaman asam sitrat, pemanis buatan (sukralosa 15 mg/saji, asesulfam-K 25 mg/saji), pewarna makanan kuning FCF.";
    }
  }

  async function handleScan() {
    errorMsg = null;
    result = null;

    if (activeTab === 'camera' || activeTab === 'upload') {
      if (!selectedFile) {
        errorMsg = 'Silakan pilih foto kemasan atau jepret gambar terlebih dahulu.';
        return;
      }
    } else {
      if (!textInput.trim()) {
        errorMsg = 'Silakan masukkan teks komposisi dan informasi nilai gizi kemasan.';
        return;
      }
    }

    loading = true;

    try {
      let res;
      if (activeTab === 'camera' || activeTab === 'upload') {
        if (!selectedFile) throw new Error('File foto belum tersedia');
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('profil_alergi', JSON.stringify(userAllergies));
        formData.append('fokus_diabetes', String(focusDiabetes));
        formData.append('fokus_hipertensi', String(focusHipertensi));
        formData.append('fokus_lemak', String(focusLemak));

        res = await fetch('/api/scan-image', {
          method: 'POST',
          body: formData
        });
      } else {
        res = await fetch('/api/scan-text', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            komposisi_teks: textInput,
            profil_alergi: userAllergies,
            fokus_diabetes: focusDiabetes,
            fokus_hipertensi: focusHipertensi,
            fokus_lemak: focusLemak
          })
        });
      }

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server error: ${res.status}`);
      }

      result = await res.json();
      
      // Scroll smoothly to results card
      setTimeout(() => {
        const el = document.getElementById('section-hasil-audit');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 150);

    } catch (err: any) {
      errorMsg = err.message || 'Gagal menghubungi server backend. Pastikan server aktif di port 8000.';
    } finally {
      loading = false;
    }
  }

  function resetAudit() {
    result = null;
    selectedFile = null;
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      previewUrl = null;
    }
    textInput = '';
    stopCamera();
    activeTab = 'upload';
  }

  function scrollToScanner() {
    const el = document.getElementById('interactive-scanner-section');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  }

  function getStatusTheme(status: string) {
    switch (status) {
      case 'AMAN':
        return {
          bg: '#f0fdf4',
          border: '#4ade80',
          textColor: '#15803d',
          title: 'PRODUK DINILAI AMAN',
          desc: 'Komposisi tidak mengandung alergen yang Anda hindari dan kandungan GGL masih dalam batas wajar.',
          icon: CheckCircle2
        };
      case 'PERINGATAN':
        return {
          bg: '#fffbeb',
          border: '#f59e0b',
          textColor: '#b45309',
          title: 'PERHATIAN: KONSUMSI TERBATAS',
          desc: 'Kandungan Gula, Garam, atau Lemak berada di kategori Waspada bagi kondisi metabolik Anda.',
          icon: AlertTriangle
        };
      case 'BAHAYA':
        return {
          bg: '#fef2f2',
          border: '#f87171',
          textColor: '#b91c1c',
          title: 'RISIKO TINGGI BAGI PROFIL ANDA',
          desc: 'Terdeteksi bahan alergen yang Anda hindari atau kadar GGL melebihi batas toleransi harian.',
          icon: AlertOctagon
        };
      default:
        return {
          bg: '#f8fafc',
          border: '#94a3b8',
          textColor: '#1e293b',
          title: 'HASIL AUDIT KOMPOSISI',
          desc: 'Berikut rincian hasil pemeriksaan komposisi bahan dan nilai gizi produk.',
          icon: ShieldCheck
        };
    }
  }

  function getGGLColor(status: string) {
    if (status === 'BERLEBIH') return { fill: '#dc2626', text: '#b91c1c', bg: '#fef2f2', border: '#fca5a5' };
    if (status === 'WASPADA') return { fill: '#d97706', text: '#b45309', bg: '#fffbeb', border: '#fcd34d' };
    return { fill: '#16a34a', text: '#15803d', bg: '#f0fdf4', border: '#86efac' };
  }

  function getGGLBadgeStyle(status: string) {
    const c = getGGLColor(status);
    return `background-color: ${c.bg}; color: ${c.text}; border-color: ${c.border};`;
  }

  function getGGLFillStyle(percent: number | null, status: string) {
    const c = getGGLColor(status);
    const w = Math.min(percent || 0, 100);
    return `width: ${w}%; background-color: ${c.fill};`;
  }
</script>

<div class="saas-grid-bg min-h-screen relative overflow-hidden">
  
  <!-- Ambient Colorful Mesh Glows (Like Bartoon SaaS Design) -->
  <div class="ambient-glow-left"></div>
  <div class="ambient-glow-right"></div>

  <!-- Top Official Reference Banner -->
  <div class="bg-stone-900 text-stone-300 text-xs py-2 px-4 text-center font-bold tracking-wide relative z-20 border-b border-stone-800">
    ⚡ RUJUKAN RESMI: PERMENKES NO. 30/2013 & PERATURAN BPOM NO. 31/2018 &nbsp;•&nbsp; INSTITUT TEKNOLOGI KALIMANTAN (ITK)
  </div>

  <!-- SaaS Navigation Bar (Bartoon Style) -->
  <nav class="saas-nav">
    <a href="/" class="saas-brand">
      <div class="saas-brand-icon">
        <Sparkles size={20} />
      </div>
      <div>
        <span class="saas-brand-name">AlerGizi</span>
        <span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 ml-1.5 border border-emerald-300">
          AI Edition
        </span>
      </div>
    </a>

    <div class="saas-nav-links">
      <a href="#fitur">Fitur AI</a>
      <a href="#alergen">10 Alergen BPOM</a>
      <a href="#ggl">Batas GGL</a>
      <a href="#akademik">Tentang ITK</a>
    </div>

    <div>
      <button type="button" on:click={scrollToScanner} class="saas-btn-nav">
        <span>Coba Scanner</span>
        <ArrowRight size={15} />
      </button>
    </div>
  </nav>

  <!-- ================================================================= -->
  <!-- HERO SECTION: MODERN SAAS LANDING PAGE (BARTOON INSPIRATION) -->
  <!-- ================================================================= -->
  <header class="saas-hero-section">
    
    <!-- Trust Pill Badge -->
    <div class="saas-trust-pill">
      <span class="flex items-center text-amber-500">★★★★★</span>
      <span>Terverifikasi BPOM RI No. 31/2018 & Permenkes No. 30/2013</span>
    </div>

    <!-- Punchy Bold Main Title (No Italic Slant!) -->
    <h1 class="saas-hero-title">
      Pangan Aman & Sehat dalam Satu Genggaman Cerdas!
    </h1>

    <!-- Subtitle -->
    <p class="saas-hero-subtitle">
      Asisten cerdas berbasis AI Vision Google Gemini 3.5 & mesin kalkulasi deterministik. Memeriksa komposisi kemasan, mendeteksi 10 alergen tersembunyi, dan memantau kuota konsumsi Gula-Garam-Lemak secara akurat.
    </p>

    <!-- Call to Action Buttons (Bartoon Style) -->
    <div class="saas-cta-row">
      <button type="button" on:click={scrollToScanner} class="btn-pill-primary">
        <span>Mulai Audit Pangan Sekarang</span>
        <ArrowRight size={17} />
      </button>

      <button type="button" on:click={scrollToScanner} class="btn-pill-secondary">
        <span>Lihat Demo Interaktif</span>
        <ChevronDown size={17} />
      </button>
    </div>

    <!-- 4 Dashboard Metric Quick Stats (Bartoon SaaS Metric Cards) -->
    <div class="stats-cards-grid">
      <div class="stat-metric-card">
        <div class="stat-metric-label">10 Alergen BPOM</div>
        <div class="stat-metric-val">100%</div>
        <span class="stat-metric-badge bg-emerald-100 text-emerald-800">Standar Pasal 41</span>
      </div>

      <div class="stat-metric-card">
        <div class="stat-metric-label">Batas Gula (G4)</div>
        <div class="stat-metric-val">50g</div>
        <span class="stat-metric-badge bg-amber-100 text-amber-800">Maks. 4 Sdm/Hari</span>
      </div>

      <div class="stat-metric-card">
        <div class="stat-metric-label">Batas Garam (G1)</div>
        <div class="stat-metric-val">2.000mg</div>
        <span class="stat-metric-badge bg-rose-100 text-rose-800">Maks. 1 Sdt/Hari</span>
      </div>

      <div class="stat-metric-card">
        <div class="stat-metric-label">Batas Lemak (L5)</div>
        <div class="stat-metric-val">67g</div>
        <span class="stat-metric-badge bg-orange-100 text-orange-800">Maks. 5 Sdm Minyak</span>
      </div>
    </div>

  </header>

  <!-- ================================================================= -->
  <!-- DEVICE SWITCHER BAR (INSTANT MOBILE VIEW IN ANTIGRAVITY!) -->
  <!-- ================================================================= -->
  <div class="relative z-10 px-4 mb-4">
    <div class="device-toggle-bar">
      <button 
        type="button" 
        class="device-toggle-btn {viewMode === 'mobile' ? 'active' : ''}"
        on:click={() => viewMode = 'mobile'}
      >
        <Smartphone size={16} />
        <span>Tampilan Ponsel (Mobile Frame)</span>
      </button>

      <button 
        type="button" 
        class="device-toggle-btn {viewMode === 'desktop' ? 'active' : ''}"
        on:click={() => viewMode = 'desktop'}
      >
        <Monitor size={16} />
        <span>Tampilan Penuh (Full Width)</span>
      </button>
    </div>
  </div>

  <!-- ================================================================= -->
  <!-- INTERACTIVE SCANNER APPLICATION (CONTAINER WRAPPER) -->
  <!-- ================================================================= -->
  <main id="interactive-scanner-section" class="relative z-10 px-3 pb-12">
    
    <!-- WRAPPER: EITHER REALISTIC SMARTPHONE FRAME OR FULL WIDTH DESKTOP -->
    <div class={viewMode === 'mobile' ? 'phone-mockup-wrapper' : 'fullwidth-dashboard-wrapper'}>
      
      <!-- If in Mobile Frame Mode: Show Phone Bezel & Dynamic Island -->
      {#if viewMode === 'mobile'}
        <div class="phone-notch-bar">
          <span>09:41</span>
          <div class="phone-dynamic-island"></div>
          <span class="flex items-center gap-1">5G 📶 100%</span>
        </div>
      {/if}

      <!-- Screen Canvas Content -->
      <div class={viewMode === 'mobile' ? 'phone-inner-screen' : ''}>
        
        <!-- Error Alert Message -->
        {#if errorMsg}
          <div class="mb-5 p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs font-semibold flex items-center gap-2.5">
            <AlertOctagon size={18} class="text-red-600 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>
        {/if}

        <!-- ================================================================= -->
        <!-- STEP 1: MASUKAN LABEL PANGAN (DEFAULT: UPLOAD GALLERY/FILE!) -->
        <!-- ================================================================= -->
        <section class="saas-step-card">
          <div class="saas-step-header">
            <span class="saas-step-badge">1</span>
            <div class="flex-1">
              <h2 class="saas-step-title">Masukan Label Pangan</h2>
              <p class="text-xs text-slate-500">Pilih berkas galeri, jepret foto langsung, atau gunakan contoh cepat.</p>
            </div>
          </div>

          <!-- Tabs: DEFAULT TO UPLOAD -->
          <div class="saas-tab-row">
            <button 
              type="button" 
              class="saas-tab-btn {activeTab === 'upload' ? 'active' : ''}" 
              on:click={() => setTab('upload')}
            >
              <Upload size={14} />
              <span>Unggah Galeri/File</span>
            </button>

            <button 
              type="button" 
              class="saas-tab-btn {activeTab === 'camera' ? 'active' : ''}" 
              on:click={() => setTab('camera')}
            >
              <Camera size={14} />
              <span>Kamera Langsung</span>
            </button>

            <button 
              type="button" 
              class="saas-tab-btn {activeTab === 'text' ? 'active' : ''}" 
              on:click={() => setTab('text')}
            >
              <FileText size={14} />
              <span>Ketik Teks</span>
            </button>
          </div>

          <!-- TAB 1: UPLOAD FILE (DEFAULT & SAFE - NO AUTO CAMERA!) -->
          {#if activeTab === 'upload'}
            <div>
              <button 
                type="button"
                class="border-2 border-dashed border-slate-300 hover:border-slate-500 rounded-2xl p-6 sm:p-8 text-center cursor-pointer transition bg-slate-50 w-full"
                on:click={() => document.getElementById('foodLabelFileInput')?.click()}
              >
                <input 
                  id="foodLabelFileInput" 
                  type="file" 
                  accept="image/*" 
                  capture="environment"
                  class="hidden" 
                  on:change={handleFileSelect} 
                />

                {#if previewUrl}
                  <div class="relative">
                    <img src={previewUrl} alt="Pratinjau Foto Label" class="max-h-56 mx-auto rounded-xl object-contain shadow mb-3" />
                    <span class="text-xs font-bold text-red-600 underline">Ganti Foto Kemasan Lain</span>
                  </div>
                {:else}
                  <div class="py-3">
                    <div class="w-12 h-12 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center mx-auto mb-2.5">
                      <Upload size={22} />
                    </div>
                    <p class="text-sm font-bold text-slate-800 mb-0.5">Pilih Foto Kemasan Makanan</p>
                    <p class="text-[11px] text-slate-500">Mendukung JPG, PNG, WEBP. Di smartphone otomatis membuka kamera bawaan HP.</p>
                  </div>
                {/if}
              </button>
            </div>

          <!-- TAB 2: LIVE WEBRTC CAMERA (ONLY STARTS WHEN EXPLICITLY OPENED) -->
          {:else if activeTab === 'camera'}
            <div>
              {#if previewUrl}
                <div class="relative rounded-2xl overflow-hidden border border-slate-300 bg-black aspect-video flex items-center justify-center mb-3">
                  <img src={previewUrl} alt="Foto Kemasan Makanan" class="w-full h-full object-contain" />
                  <div class="absolute top-3 right-3 bg-emerald-700 text-white text-xs font-bold px-2.5 py-1 rounded-md shadow">
                    ✓ Foto Siap Diaudit
                  </div>
                </div>

                <button 
                  type="button" 
                  on:click={retakePhoto}
                  class="w-full py-2.5 px-4 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold flex items-center justify-center gap-2 border border-slate-300 transition"
                >
                  <RotateCcw size={14} />
                  <span>Ambil Ulang Foto</span>
                </button>

              {:else if cameraActive}
                <div class="relative w-full aspect-video max-h-72 bg-black rounded-xl overflow-hidden border-2 border-slate-800 mb-3">
                  <!-- svelte-ignore a11y_media_has_caption -->
                  <video 
                    bind:this={videoElement} 
                    playsinline 
                    autoplay 
                    muted 
                    class="w-full h-full object-cover"
                  ></video>
                  <div class="absolute inset-8 border-2 border-dashed border-white/80 rounded-lg pointer-events-none"></div>
                  <div class="absolute bottom-2 left-2 bg-black/75 px-2.5 py-1 rounded text-[11px] text-white">
                    Arahkan ke tabel komposisi & nilai gizi
                  </div>
                </div>

                <div class="flex items-center gap-2">
                  <button 
                    type="button" 
                    on:click={capturePhoto} 
                    disabled={isCapturing}
                    class="flex-1 py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs flex items-center justify-center gap-2 transition"
                  >
                    <Camera size={16} />
                    <span>{isCapturing ? 'Menyimpan Foto...' : 'Ambil Foto Sekarang'}</span>
                  </button>

                  <button 
                    type="button" 
                    on:click={switchCamera}
                    title="Ganti Kamera Depan / Belakang"
                    class="p-3 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-300 transition"
                  >
                    <RefreshCw size={16} />
                  </button>
                </div>

              {:else}
                <div class="p-6 rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 text-center">
                  {#if cameraError}
                    <p class="text-xs text-red-700 mb-2 font-bold">{cameraError}</p>
                  {/if}
                  <button 
                    type="button" 
                    on:click={startCamera}
                    class="py-2.5 px-5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold inline-flex items-center gap-2 shadow"
                  >
                    <Camera size={15} />
                    <span>Buka Kamera Sekarang</span>
                  </button>
                  <p class="text-[11px] text-slate-500 mt-2">Gunakan kamera webcam laptop atau kamera HP Anda.</p>
                </div>
              {/if}
            </div>

          <!-- TAB 3: TEXT INPUT WITH ONE-CLICK SAMPLES -->
          {:else}
            <div>
              <textarea 
                rows="5"
                class="w-full bg-white border border-slate-300 rounded-xl p-3 text-xs text-slate-800 font-mono placeholder:text-slate-400 mb-2.5 resize-none leading-relaxed focus:outline-none focus:border-slate-800"
                placeholder="Ketik atau tempelkan teks daftar komposisi bahan dan nilai gizi di sini..."
                bind:value={textInput}
              ></textarea>

              <div class="flex items-center gap-1.5 flex-wrap">
                <span class="text-[11px] text-slate-500 font-bold">Contoh Cepat:</span>
                <button type="button" on:click={() => loadSample('biscuit')} class="text-[11px] px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium border border-slate-300 transition">
                  Biskuit Susu (Alergen)
                </button>
                <button type="button" on:click={() => loadSample('soda')} class="text-[11px] px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium border border-slate-300 transition">
                  Soda (Gula 33g)
                </button>
                <button type="button" on:click={() => loadSample('diet')} class="text-[11px] px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium border border-slate-300 transition">
                  Sirup Sukralosa
                </button>
              </div>
            </div>
          {/if}
        </section>

        <!-- ================================================================= -->
        <!-- STEP 2: PROFIL RISIKO KONSUMEN (10 ALERGEN & GGL) -->
        <!-- ================================================================= -->
        <section class="saas-step-card">
          <div class="saas-step-header">
            <span class="saas-step-badge">2</span>
            <div class="flex-1">
              <h2 class="saas-step-title">Profil Risiko Konsumen</h2>
              <p class="text-xs text-slate-500">Pilih alergi yang Anda hindari dan batasan nutrisi medis Anda.</p>
            </div>
          </div>

          <!-- 2.1: 10 Alergen BPOM -->
          <div class="mb-6">
            <div class="flex items-center justify-between mb-2.5">
              <label class="text-xs font-bold text-slate-900">
                10 Alergen Wajib BPOM RI (Pasal 41)
              </label>
              <span class="text-[11px] text-slate-400">Klik untuk memilih</span>
            </div>

            <div class="saas-allergen-grid">
              {#each allergenOptions as opt}
                <button 
                  type="button" 
                  class="saas-allergen-item {userAllergies.includes(opt.id) ? 'selected' : ''}"
                  on:click={() => toggleAllergy(opt.id)}
                >
                  <span class="text-xl flex-shrink-0">{opt.icon}</span>
                  <div class="flex-1 min-w-0">
                    <div class="text-xs font-bold text-slate-900 flex items-center justify-between">
                      <span>{opt.label}</span>
                      {#if userAllergies.includes(opt.id)}
                        <span class="text-[10px] font-extrabold text-red-700 bg-red-100 px-1.5 py-0.5 rounded-full">Dipantau</span>
                      {/if}
                    </div>
                    <div class="text-[10px] text-slate-500 truncate">{opt.sub}</div>
                  </div>
                </button>
              {/each}
            </div>

            <!-- 2.1b: Alergi Kustom / Tambahan (Non-BPOM, e.g. Ayam, Sapi, Wijen) -->
            <div class="mt-4 pt-3.5 border-t border-slate-200">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                  <span>🍗</span>
                  <span>Alergi Spesifik Lainnya (Fleksibel / Kustom)</span>
                </span>
                <span class="text-[10px] text-slate-400">Non-BPOM didukung AI</span>
              </div>
              <p class="text-[11px] text-slate-500 mb-2.5">
                Punya alergi spesifik di luar 10 daftar wajib BPOM? Pilih cepat atau ketik sendiri:
              </p>

              <!-- Quick Chips -->
              <div class="flex flex-wrap gap-1.5 mb-3">
                {#each [
                  { id: 'Ayam', label: '🍗 Daging Ayam' },
                  { id: 'Daging Sapi', label: '🥩 Daging Sapi' },
                  { id: 'Wijen', label: '🌱 Biji Wijen' },
                  { id: 'Jagung', label: '🌽 Jagung' },
                  { id: 'Madu', label: '🍯 Madu' }
                ] as chip}
                  <button
                    type="button"
                    class="text-xs px-2.5 py-1 rounded-lg border transition font-medium {userAllergies.includes(chip.id) ? 'bg-amber-100 border-amber-300 text-amber-900 font-bold' : 'bg-slate-100 border-slate-200 text-slate-700 hover:bg-slate-200'}"
                    on:click={() => toggleAllergy(chip.id)}
                  >
                    {chip.label} {userAllergies.includes(chip.id) ? '✓' : '+'}
                  </button>
                {/each}
              </div>

              <!-- Input Bebas -->
              <div class="flex gap-2">
                <input
                  type="text"
                  placeholder="Ketik alergi lain (misal: Stroberi, Cokelat)..."
                  bind:value={customAllergyInput}
                  on:keydown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addCustomAllergy(); } }}
                  class="flex-1 bg-white border border-slate-300 rounded-xl px-3 py-1.5 text-xs text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-slate-800"
                />
                <button
                  type="button"
                  on:click={addCustomAllergy}
                  class="px-3.5 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold transition flex-shrink-0"
                >
                  Tambah
                </button>
              </div>

              <!-- Active Custom Allergens Badges -->
              {#if userAllergies.some(a => !allergenOptions.map(o => o.id).includes(a))}
                <div class="flex flex-wrap items-center gap-1.5 mt-2.5">
                  <span class="text-[10px] font-bold text-slate-500">Alergi Kustom Aktif:</span>
                  {#each userAllergies.filter(a => !allergenOptions.map(o => o.id).includes(a)) as custom}
                    <span class="inline-flex items-center gap-1 text-[11px] font-bold bg-amber-100 text-amber-900 px-2 py-0.5 rounded-full border border-amber-300">
                      <span>{custom}</span>
                      <button type="button" on:click={() => removeAllergy(custom)} class="hover:text-red-700 ml-0.5">×</button>
                    </span>
                  {/each}
                </div>
              {/if}
            </div>
          </div>

          <!-- 2.2: Pembatasan Nutrisi GGL (G4-G1-L5) -->
          <div>
            <div class="mb-3">
              <label class="text-xs font-bold text-slate-900 block">
                Pembatasan Khusus Penyakit Degeneratif (Permenkes 30/2013)
              </label>
              <p class="text-[11px] text-slate-500">Pilih kondisi kesehatan untuk pengawasan ketat ambang batas harian.</p>
            </div>

            <div class="saas-metabolic-grid">
              
              <!-- 1. Gula -->
              <button 
                type="button" 
                class="saas-metabolic-card {focusDiabetes ? 'checked' : ''}"
                on:click={() => focusDiabetes = !focusDiabetes}
              >
                <div>
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                      <Droplet size={15} class="text-amber-600" />
                      <span>Batasi Gula</span>
                    </span>
                    <span class="w-4 h-4 rounded border flex items-center justify-center text-[10px] font-bold {focusDiabetes ? 'bg-emerald-600 text-white border-emerald-600' : 'border-slate-300 bg-white'}">
                      {#if focusDiabetes}✓{/if}
                    </span>
                  </div>
                  <span class="text-[11px] font-bold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded">Maks. 50g / 4 sdm</span>
                </div>
                <div class="text-[11px] text-slate-600 mt-2.5 pt-2 border-t border-slate-200">
                  <strong>Kenapa segitu?</strong> Melebihi 50g (10% kalori harian) memicu resistensi insulin dan penumpukan lemak hati, pemicu utama <strong>Diabetes Melitus Tipe 2</strong>.
                </div>
              </button>

              <!-- 2. Garam -->
              <button 
                type="button" 
                class="saas-metabolic-card {focusHipertensi ? 'checked' : ''}"
                on:click={() => focusHipertensi = !focusHipertensi}
              >
                <div>
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                      <HeartPulse size={15} class="text-rose-600" />
                      <span>Batasi Garam</span>
                    </span>
                    <span class="w-4 h-4 rounded border flex items-center justify-center text-[10px] font-bold {focusHipertensi ? 'bg-emerald-600 text-white border-emerald-600' : 'border-slate-300 bg-white'}">
                      {#if focusHipertensi}✓{/if}
                    </span>
                  </div>
                  <span class="text-[11px] font-bold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded">Maks. 2.000mg Natrium</span>
                </div>
                <div class="text-[11px] text-slate-600 mt-2.5 pt-2 border-t border-slate-200">
                  <strong>Kenapa segitu?</strong> Kelebihan ion natrium menahan air dalam pembuluh darah, memicu lonjakan volume darah dan tekanan arteri (<strong>Hipertensi</strong>), stroke, dan gagal ginjal.
                </div>
              </button>

              <!-- 3. Lemak -->
              <button 
                type="button" 
                class="saas-metabolic-card {focusLemak ? 'checked' : ''}"
                on:click={() => focusLemak = !focusLemak}
              >
                <div>
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                      <Flame size={15} class="text-orange-600" />
                      <span>Batasi Lemak</span>
                    </span>
                    <span class="w-4 h-4 rounded border flex items-center justify-center text-[10px] font-bold {focusLemak ? 'bg-emerald-600 text-white border-emerald-600' : 'border-slate-300 bg-white'}">
                      {#if focusLemak}✓{/if}
                    </span>
                  </div>
                  <span class="text-[11px] font-bold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded">Maks. 67g / 5 sdm</span>
                </div>
                <div class="text-[11px] text-slate-600 mt-2.5 pt-2 border-t border-slate-200">
                  <strong>Kenapa segitu?</strong> Asupan lemak berlebih memicu peningkatan kolesterol LDL dan plak aterosklerosis yang menyumbat arteri (<strong>Penyakit Jantung Koroner</strong>).
                </div>
              </button>

            </div>
          </div>
        </section>

        <!-- ================================================================= -->
        <!-- ACTION BUTTON (BIG BLACK PILL) -->
        <!-- ================================================================= -->
        <button 
          type="button" 
          class="btn-saas-audit"
          on:click={handleScan}
          disabled={loading}
        >
          {#if loading}
            <RefreshCw size={20} class="animate-spin text-emerald-400" />
            <span>Sedang Memeriksa dengan Gemini 3.5...</span>
          {:else}
            <ShieldCheck size={20} class="text-emerald-400" />
            <span>Audit Keamanan Pangan Sekarang</span>
            <ArrowRight size={18} />
          {/if}
        </button>

        <!-- ================================================================= -->
        <!-- STEP 3: LAPORAN HASIL AUDIT (LEGA, TEGAK, TINGGI KONTRAS) -->
        <!-- ================================================================= -->
        {#if result}
          {@const theme = getStatusTheme(result.status_keamanan_umum)}
          {@const IconComponent = theme.icon}

          <section id="section-hasil-audit" class="saas-step-card border-slate-300">
            
            <!-- Header Sertifikat Laporan -->
            <div class="flex items-center justify-between border-b border-slate-200 pb-4 mb-5">
              <div class="flex items-center gap-2.5">
                <span class="saas-step-badge bg-emerald-700">3</span>
                <div>
                  <h3 class="text-base font-extrabold text-slate-900">Sertifikat Hasil Audit Pangan</h3>
                  <p class="text-[11px] text-slate-500">Standar BPOM No. 31/2018 & Permenkes No. 30/2013</p>
                </div>
              </div>

              <div class="flex items-center gap-2">
                <button 
                  type="button" 
                  on:click={() => window.print()}
                  class="p-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold flex items-center gap-1 border border-slate-300"
                  title="Cetak Laporan PDF"
                >
                  <Printer size={15} />
                  <span class="hidden sm:inline">Cetak</span>
                </button>
                <button 
                  type="button" 
                  on:click={resetAudit}
                  class="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold flex items-center gap-1"
                  title="Audit Produk Lain"
                >
                  <RotateCcw size={15} />
                  <span class="hidden sm:inline">Reset</span>
                </button>
              </div>
            </div>

            <!-- Status Banner -->
            <div 
              class="p-4 rounded-2xl border-2 mb-5 flex items-start gap-3.5"
              style="background-color: {theme.bg}; border-color: {theme.border};"
            >
              <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0" style="background-color: {theme.border};">
                <IconComponent size={24} style="color: {theme.textColor};" />
              </div>
              <div>
                <span class="text-[11px] font-extrabold tracking-wider uppercase block" style="color: {theme.textColor};">
                  {theme.title}
                </span>
                <h4 class="text-base sm:text-lg font-extrabold text-slate-900 mt-0.5">
                  {result.nama_produk}
                </h4>
                <p class="text-xs text-slate-700 font-medium mt-1">
                  {theme.desc}
                </p>
              </div>
            </div>

            <!-- Ringkasan Eksekutif -->
            <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 mb-5">
              <h5 class="text-xs font-bold text-slate-900 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                <span>📋 Ringkasan Analisis AI & Klinis</span>
              </h5>
              <p class="text-xs sm:text-sm text-slate-800 leading-relaxed">
                {result.ringkasan_eksekutif}
              </p>
            </div>

            <!-- Alergen BPOM Table -->
            <div class="p-4 rounded-xl bg-white border border-slate-200 mb-5">
              <div class="flex items-center justify-between mb-3 flex-wrap gap-1">
                <h5 class="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                  <AlertTriangle size={15} class="text-amber-600" />
                  <span>Pemeriksaan 10 Alergen BPOM RI</span>
                </h5>
                
                <div class="flex items-center gap-1 flex-wrap">
                  {#if userAllergies.length === 0}
                    <span class="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-bold border border-slate-200">Bebas Alergi</span>
                  {:else}
                    {#each userAllergies as a}
                      <span class="text-[10px] px-2 py-0.5 rounded-full bg-red-100 text-red-800 font-extrabold border border-red-200">⚠️ {a}</span>
                    {/each}
                  {/if}
                </div>
              </div>

              {#if result.alergen_terdeteksi.length === 0}
                <div class="p-3.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs flex items-center gap-2">
                  <CheckCircle2 size={18} class="text-emerald-600 flex-shrink-0" />
                  <span><strong>Bersih dari Alergen:</strong> Tidak ditemukan bahan alergen pangan wajib BPOM dalam produk ini.</span>
                </div>
              {:else}
                <div class="overflow-x-auto">
                  <table class="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr class="border-b border-slate-200 text-slate-500 font-bold bg-slate-50">
                        <th class="py-2 px-2.5">Bahan</th>
                        <th class="py-2 px-2.5">Kategori BPOM</th>
                        <th class="py-2 px-2.5">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {#each result.alergen_terdeteksi as item}
                        {@const isUserRisk = userAllergies.some(a => item.kategori_alergen.toLowerCase().includes(a.toLowerCase()) || item.bahan.toLowerCase().includes(a.toLowerCase()))}
                        <tr class="border-b border-slate-100 hover:bg-slate-50">
                          <td class="py-2.5 px-2.5 font-bold text-slate-900">{item.bahan}</td>
                          <td class="py-2.5 px-2.5 text-slate-700">{item.kategori_alergen}</td>
                          <td class="py-2.5 px-2.5">
                            {#if isUserRisk}
                              <span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-red-100 text-red-800 border border-red-300">
                                ⚠️ Alergi Anda!
                              </span>
                            {:else}
                              <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-300">
                                Waspada
                              </span>
                            {/if}
                          </td>
                        </tr>
                      {/each}
                    </tbody>
                  </table>
                </div>
              {/if}
            </div>

            <!-- Evaluasi GGL Kemenkes (3 Spacious Cards) -->
            <div class="p-4 rounded-xl bg-white border border-slate-200 mb-5">
              <div class="flex items-center justify-between mb-3.5">
                <div>
                  <h5 class="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                    <Activity size={15} class="text-blue-600" />
                    <span>Batas Konsumsi GGL (Permenkes No. 30/2013)</span>
                  </h5>
                  <p class="text-[11px] text-slate-500">Takaran saji: <strong>{result.analisis_ggl.takaran_saji_gram ? `${result.analisis_ggl.takaran_saji_gram}g` : 'Standar'}</strong> per porsi</p>
                </div>
                <span class="text-[10px] font-bold px-2 py-1 rounded bg-slate-100 text-slate-700 border border-slate-200">
                  G4-G1-L5
                </span>
              </div>

              <!-- Gula -->
              <div class="saas-ggl-box">
                <div class="flex items-center justify-between">
                  <span class="text-xs font-bold text-slate-900">Gula: {result.analisis_ggl.gula_gram ?? 0}g</span>
                  <span class="text-[10px] font-bold px-2 py-0.5 rounded-full border" style={getGGLBadgeStyle(result.analisis_ggl.status_gula)}>
                    {result.analisis_ggl.persen_gula_harian?.toFixed(1)}% ({result.analisis_ggl.status_gula})
                  </span>
                </div>
                <div class="saas-progress-track">
                  <div class="saas-progress-fill" style={getGGLFillStyle(result.analisis_ggl.persen_gula_harian, result.analisis_ggl.status_gula)}></div>
                </div>
                <p class="text-[10px] text-slate-500">Batas harian: Maks. 50g (4 sdm). Porsi ini menghabiskan {result.analisis_ggl.persen_gula_harian?.toFixed(1)}% kuota gula aman.</p>
              </div>

              <!-- Garam / Natrium -->
              <div class="saas-ggl-box">
                <div class="flex items-center justify-between">
                  <span class="text-xs font-bold text-slate-900">Garam / Natrium: {result.analisis_ggl.natrium_mg ?? 0}mg</span>
                  <span class="text-[10px] font-bold px-2 py-0.5 rounded-full border" style={getGGLBadgeStyle(result.analisis_ggl.status_natrium)}>
                    {result.analisis_ggl.persen_natrium_harian?.toFixed(1)}% ({result.analisis_ggl.status_natrium})
                  </span>
                </div>
                <div class="saas-progress-track">
                  <div class="saas-progress-fill" style={getGGLFillStyle(result.analisis_ggl.persen_natrium_harian, result.analisis_ggl.status_natrium)}></div>
                </div>
                <p class="text-[10px] text-slate-500">Batas harian: Maks. 2.000mg (1 sdt). Porsi ini menghabiskan {result.analisis_ggl.persen_natrium_harian?.toFixed(1)}% kuota natrium.</p>
              </div>

              <!-- Lemak Total -->
              <div class="saas-ggl-box">
                <div class="flex items-center justify-between">
                  <span class="text-xs font-bold text-slate-900">Lemak Total: {result.analisis_ggl.lemak_total_gram ?? 0}g</span>
                  <span class="text-[10px] font-bold px-2 py-0.5 rounded-full border" style={getGGLBadgeStyle(result.analisis_ggl.status_lemak)}>
                    {result.analisis_ggl.persen_lemak_harian?.toFixed(1)}% ({result.analisis_ggl.status_lemak})
                  </span>
                </div>
                <div class="saas-progress-track">
                  <div class="saas-progress-fill" style={getGGLFillStyle(result.analisis_ggl.persen_lemak_harian, result.analisis_ggl.status_lemak)}></div>
                </div>
                <p class="text-[10px] text-slate-500">Batas harian: Maks. 67g (5 sdm). Porsi ini menghabiskan {result.analisis_ggl.persen_lemak_harian?.toFixed(1)}% kuota lemak.</p>
              </div>
            </div>

            <!-- Pemanis Buatan (Jika ada) -->
            {#if result.pemanis_buatan.terdeteksi}
              <div class="p-4 rounded-xl bg-amber-50 border border-amber-300 mb-5">
                <div class="flex items-center gap-2 text-xs font-bold text-amber-900 mb-1.5">
                  <AlertTriangle size={15} class="text-amber-700" />
                  <span>Peringatan Pemanis Buatan (BPOM No. 11/2019)</span>
                </div>
                <div class="flex items-center gap-1 mb-2">
                  {#each result.pemanis_buatan.jenis_pemanis as jn}
                    <span class="text-[10px] px-2 py-0.5 rounded bg-amber-200 text-amber-900 font-bold border border-amber-300">{jn}</span>
                  {/each}
                </div>
                <p class="text-xs text-amber-900 font-medium leading-relaxed bg-white/70 p-2.5 rounded-lg border border-amber-200">
                  Peringatan Resmi BPOM: "{result.pemanis_buatan.peringatan_wajib}"
                </p>
              </div>
            {/if}

            <!-- Saran Konsumen -->
            <div class="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <h5 class="text-xs font-bold text-slate-900 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                <span>💡 Saran untuk Konsumen</span>
              </h5>
              <p class="text-xs sm:text-sm text-slate-800 leading-relaxed">
                {result.rekomendasi_konsumen}
              </p>
            </div>

          </section>
        {/if}

      </div>
    </div>
  </main>

  <!-- ================================================================= -->
  <!-- ACADEMIC FOOTER (INSTITUT TEKNOLOGI KALIMANTAN) -->
  <!-- ================================================================= -->
  <footer id="akademik" class="saas-footer relative z-10">
    <p class="text-sm font-extrabold text-slate-900 mb-1">
      Institut Teknologi Kalimantan (ITK) • Program Studi Sistem Informasi
    </p>
    <p class="text-xs font-semibold text-slate-700 mb-2">
      Mata Kuliah: Kapita Selekta - AI Engineering &nbsp;|&nbsp; Dosen Pengampu: <strong>Aidil Saputra Kirsan, S.ST., M.Tr.Kom.</strong>
    </p>
    <p class="text-xs text-slate-500 max-w-xl mx-auto leading-relaxed">
      Sistem audit terintegrasi memadukan penglihatan cerdas Google Gemini 3.5 dengan mesin kalkulasi deterministik bebas halusinasi berbasis Permenkes No. 30/2013 dan Peraturan BPOM No. 31/2018.
    </p>
  </footer>

</div>
