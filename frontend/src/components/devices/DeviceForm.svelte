<script>
  import { api } from '../../stores/api';
  import { notify } from '../../stores/auth';

  // Props
  export let customers = [];
  export let selectedCustomerId = '';
  export let selectedCustomer = null;
  export let showCustomerForm = false;
  export let customerForm = {
    name: '',
    email: '',
    phone: '',
    whatsapp: '',
    telegram: '',
    address: ''
  };
  export let deviceForm = {
    brand: '',
    model: '',
    serial_number: '',
    imei: '',
    device_type: 'smartphone',
    color: '',
    storage: '',
    password_pattern: '',
    accessories: '',
    description: ''
  };
  export let photos = [];
  export let isEditing = false;
  export let editingDeviceId = null;
  export let submitLabel = 'Guardar Dispositivo';
  export let showDescription = false;
  export let showPhotos = true;
  
  // Callbacks
  export let onSubmit = () => {};
  export let onClose = () => {};

  const deviceTypes = [
    { value: 'smartphone', label: '📱 Smartphone' },
    { value: 'tablet', label: '📟 Tablet' },
    { value: 'laptop', label: '💻 Laptop' },
    { value: 'desktop', label: '🖥️ Desktop' },
    { value: 'console', label: '🎮 Consola' },
    { value: 'other', label: '📦 Otro' }
  ];

  // Cámara
  let showCamera = false;
  let videoElement = null;
  let cameraMode = 'photo';
  let isRecording = false;
  let mediaRecorder = null;
  let videoChunks = [];
  const MAX_IMAGE_SIZE = 5 * 1024 * 1024;
  const MAX_VIDEO_SIZE = 30 * 1024 * 1024;

  // Sincronizar selectedCustomer cuando selectedCustomerId cambia
  $: {
    if (selectedCustomerId && !showCustomerForm) {
      selectedCustomer = (customers || []).find(c => c.id === selectedCustomerId) || null;
    }
  }

  async function handleSubmit() {
    try {
      let finalCustomerId = selectedCustomerId;

      // Paso 0: Crear cliente si es nuevo
      if (showCustomerForm) {
        const missingCustomerFields = [];
        if (!customerForm.name) missingCustomerFields.push('Nombre');
        if (!customerForm.phone) missingCustomerFields.push('Teléfono');
        
        if (missingCustomerFields.length > 0) {
          notify(`Faltan campos obligatorios del cliente: ${missingCustomerFields.join(', ')}`, 'warning');
          return;
        }

        // Limpiar campos opcionales para evitar errores de validación (email vacío, etc)
        const customerData = { ...customerForm };
        if (!customerData.email) delete customerData.email;
        if (!customerData.whatsapp) delete customerData.whatsapp;
        if (!customerData.telegram) delete customerData.telegram;
        if (!customerData.address) delete customerData.address;

        const newCustomer = await api.createCustomer(customerData);
        finalCustomerId = newCustomer.id;
        selectedCustomerId = finalCustomerId;
        selectedCustomer = newCustomer;
        customers = [...customers, newCustomer];
        showCustomerForm = false; // Ocultar formulario después de crear
      } else {
        if (!finalCustomerId) {
          notify('Debe seleccionar o crear un cliente', 'warning');
          return;
        }
      }

      // Paso 1: Validar y Crear/Actualizar dispositivo
      const missingDeviceFields = [];
      if (!deviceForm.device_type) missingDeviceFields.push('Tipo de Dispositivo');
      if (!deviceForm.brand) missingDeviceFields.push('Marca');
      if (showDescription && !deviceForm.description?.trim()) missingDeviceFields.push('Descripción del Problema');

      if (missingDeviceFields.length > 0) {
        notify(`Faltan campos obligatorios del dispositivo: ${missingDeviceFields.join(', ')}`, 'warning');
        return;
      }

      const data = {
        ...deviceForm,
        customer_id: finalCustomerId,
        photos: ''  // Se actualizará después de subir las fotos
      };

      let deviceId = editingDeviceId;
      let result = {
        device: null,
        repair: null,
        customer: selectedCustomer
      };
      
      if (isEditing && deviceId) {
        result.device = await api.updateDevice(deviceId, data);
        notify('Dispositivo actualizado correctamente', 'success');
      } else {
        const device = await api.createDevice(data);
        deviceId = device.id;
        result.device = device;
        notify('Dispositivo registrado correctamente', 'success');
        
        // Si hay descripción, crear reparación (solo para POS)
        if (deviceForm.description && deviceForm.description.trim()) {
          try {
            const repairData = {
              device_id: deviceId,
              description: deviceForm.description,
              priority: deviceForm.priority || 'normal',
              estimated_cost: 0
            };
            result.repair = await api.createRepair(repairData);
          } catch (repairError) {
            console.error('Error creando reparación:', repairError);
            // No fallar si la reparación falla, el dispositivo ya se creó
          }
        }
      }

      // Paso 2: Subir fotos si hay
      if (photos.length > 0 && deviceId) {
        const uploadedUrls = [];
        
        for (const photoUrl of photos) {
          try {
            // Si es blob URL, convertir a File y subir
            if (photoUrl.startsWith('blob:')) {
              const response = await fetch(photoUrl);
              const blob = await response.blob();
              // Determinar extensión del MIME type
              let ext = '.jpg';
              if (blob.type.includes('png')) ext = '.png';
              else if (blob.type.includes('webp')) ext = '.webp';
              else if (blob.type.includes('mp4')) ext = '.mp4';
              else if (blob.type.includes('quicktime')) ext = '.mov';
              
              const filename = `photo_${Date.now()}${ext}`;
              const file = new File([blob], filename, { type: blob.type });
              
              const result = await api.uploadPhoto(deviceId, file);
              // El resultado puede ser {url: '/api/v1/uploads/photo/xxx.jpg'} o una URL directa
              uploadedUrls.push(result.url || result);
            }
            // Si ya es URL del servidor, solo agregar
            else if (photoUrl.startsWith('/api/')) {
              uploadedUrls.push(photoUrl);
            }
          } catch (error) {
            console.error('Error subiendo foto:', error);
            notify('Error subiendo una foto: ' + error.message, 'warning');
          }
        }
        
        if (uploadedUrls.length > 0) {
          // Actualizar dispositivo con las URLs de las fotos
          result.device = await api.updateDevice(deviceId, { photos: uploadedUrls.join(',') });
          notify(`${uploadedUrls.length} foto(s) guardada(s)`, 'success');
        }
      }
      
      onSubmit(result);
    } catch (error) {
      notify(error.message, 'danger');
    }
  }

  // Funciones de cámara
  async function openCamera(mode = 'photo') {
    cameraMode = mode;
    showCamera = true;
    await new Promise(resolve => setTimeout(resolve, 100));

    if (videoElement) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment' },
          audio: mode === 'video'
        });
        videoElement.srcObject = stream;

        if (mode === 'video') {
          mediaRecorder = new MediaRecorder(stream, {
            mimeType: MediaRecorder.isTypeSupported('video/webm') ? 'video/webm' : 'video/mp4'
          });

          mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) {
              videoChunks.push(event.data);
            }
          };

          mediaRecorder.onstop = async () => {
            const blob = new Blob(videoChunks, { type: 'video/mp4' });
            const videoUrl = URL.createObjectURL(blob);
            photos = [...photos, videoUrl];
            videoChunks = [];
            notify('Video grabado', 'success');
            closeCamera();
          };
        }
      } catch (error) {
        notify('Error al abrir cámara: ' + error.message, 'danger');
        showCamera = false;
      }
    }
  }

  function closeCamera() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }
    if (videoElement && videoElement.srcObject) {
      videoElement.srcObject.getTracks().forEach(track => track.stop());
    }
    showCamera = false;
  }

  async function takePhoto() {
    if (!videoElement) return;

    const canvas = document.createElement('canvas');
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;
    canvas.getContext('2d').drawImage(videoElement, 0, 0);

    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.8));
    const buffer = await blob.arrayBuffer();
    
    if (buffer.byteLength > MAX_IMAGE_SIZE) {
      notify('Imagen muy grande. Máximo 5MB', 'danger');
      return;
    }

    const photoUrl = URL.createObjectURL(blob);
    photos = [...photos, photoUrl];
    notify('Foto tomada', 'success');
  }

  async function toggleRecording() {
    if (!mediaRecorder) return;

    if (isRecording) {
      mediaRecorder.stop();
      isRecording = false;
    } else {
      videoChunks = [];
      mediaRecorder.start();
      isRecording = true;
      notify('Grabando video... (30s máx)', 'info');

      setTimeout(() => {
        if (isRecording && mediaRecorder.state !== 'inactive') {
          mediaRecorder.stop();
          isRecording = false;
          notify('Video grabado', 'success');
          closeCamera();
        }
      }, 30000);
    }
  }

  function removePhoto(index) {
    photos.splice(index, 1);
    photos = [...photos];
  }

  // Subir fotos desde archivo
  function handleFileUpload(event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    Array.from(files).forEach(file => {
      if (!file.type.startsWith('image/') && !file.type.startsWith('video/')) {
        notify('Solo se permiten imágenes y videos', 'warning');
        return;
      }

      if (file.type.startsWith('video/') && file.size > MAX_VIDEO_SIZE) {
        notify('Video muy grande. Máximo 30MB', 'danger');
        return;
      }

      if (file.type.startsWith('image/') && file.size > MAX_IMAGE_SIZE) {
        notify('Imagen muy grande. Máximo 5MB', 'danger');
        return;
      }

      const url = URL.createObjectURL(file);
      photos = [...photos, url];
    });

    notify(`${files.length} archivo(s) agregado(s)`, 'success');
    event.target.value = '';
  }
</script>

<form on:submit|preventDefault={handleSubmit}>
  <div class="custom-modal-body" style="max-height: 65vh; overflow-y: auto;">
    {#if showPhotos}
    <!-- Fotos del dispositivo -->
    <div class="form-section">
      <h4 class="section-title">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
          <circle cx="12" cy="13" r="4"/>
        </svg>
        Fotos del Dispositivo
      </h4>

      <div class="photo-actions">
        <button class="btn btn-primary btn-sm" type="button" on:click={() => openCamera('photo')}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
            <circle cx="12" cy="13" r="4"/>
          </svg>
          Tomar Foto
        </button>
        <button class="btn btn-secondary btn-sm" type="button" on:click={() => openCamera('video')}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="23 7 16 12 23 17 23 7"/>
            <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
          </svg>
          Grabar Video
        </button>
        <label class="btn btn-outline btn-sm" style="cursor: pointer;" for="device-file-upload">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
          </svg>
          Subir Archivos
          <input
            id="device-file-upload"
            name="device-file-upload"
            type="file"
            accept="image/*,video/*"
            multiple
            style="display: none;"
            on:change={handleFileUpload}
          />
        </label>
      </div>

      {#if photos.length > 0}
      <div class="photos-grid">
        {#each photos || [] as photo, index}
        <div class="photo-item">
          {#if photo.endsWith('.mp4') || photo.endsWith('.mov') || photo.includes('video')}
          <video src={photo} controls>
            <track kind="captions" />
          </video>
          {:else}
          <img src={photo} alt="Foto del dispositivo" />
          {/if}
          <button class="remove-photo" type="button" on:click={() => removePhoto(index)}>×</button>
        </div>
        {/each}
      </div>
      {:else}
      <p class="text-muted text-sm">No hay fotos tomadas. Usa la cámara o sube archivos.</p>
      {/if}
    </div>
    {/if}

    <!-- Selección de cliente -->
    <div class="form-section">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h4 class="section-title" style="margin-bottom: 0;">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
          Cliente
        </h4>
        <button type="button" class="btn btn-outline btn-sm" on:click={() => showCustomerForm = !showCustomerForm}>
          {showCustomerForm ? '🔍 Buscar Existente' : '+ Nuevo Cliente'}
        </button>
      </div>

      {#if showCustomerForm}
        <div class="form-grid">
          <div class="form-group">
            <label class="label" for="cust_name">Nombre *</label>
            <input id="cust_name" name="name" type="text" class="input" bind:value={customerForm.name} required={showCustomerForm} placeholder="Nombre completo" />
          </div>
          <div class="form-group">
            <label class="label" for="cust_phone">Teléfono *</label>
            <input id="cust_phone" name="phone" type="tel" class="input" bind:value={customerForm.phone} required={showCustomerForm} placeholder="Ej: 555-0123" />
          </div>
          <div class="form-group">
            <label class="label" for="cust_email">Email</label>
            <input id="cust_email" name="email" type="email" class="input" bind:value={customerForm.email} placeholder="correo@ejemplo.com" />
          </div>
          <div class="form-group">
            <label class="label" for="cust_wa">WhatsApp</label>
            <input id="cust_wa" name="whatsapp" type="tel" class="input" bind:value={customerForm.whatsapp} placeholder="Ej: +52 55..." />
          </div>
          <div class="form-group full-width">
            <label class="label" for="cust_tg">Telegram</label>
            <input id="cust_tg" name="telegram" type="text" class="input" bind:value={customerForm.telegram} placeholder="@usuario" />
          </div>
          <div class="form-group full-width">
            <label class="label" for="cust_addr">Dirección</label>
            <input id="cust_addr" name="address" type="text" class="input" bind:value={customerForm.address} placeholder="Dirección completa" />
          </div>
        </div>
      {:else}
        <div class="form-group">
          <label class="label" for="customer_id">Buscar Cliente *</label>
          <select id="customer_id" class="select" bind:value={selectedCustomerId} required={!showCustomerForm}>
            <option value="">Seleccionar cliente</option>
            {#each customers || [] as customer}
              <option value={customer.id}>{customer.name} - {customer.phone}</option>
            {/each}
          </select>
        </div>
      {/if}
    </div>

    <!-- Datos del dispositivo -->
    <div class="form-section">
      <h4 class="section-title">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="2" y="2" width="20" height="8" rx="2"/>
          <rect x="2" y="14" width="20" height="8" rx="2"/>
        </svg>
        Dispositivo
      </h4>

      <div class="form-grid">
        <div class="form-group">
          <label class="label" for="dev_type">Tipo de Dispositivo *</label>
          <select id="dev_type" name="device_type" class="select" bind:value={deviceForm.device_type}>
            {#each deviceTypes as type}
              <option value={type.value}>{type.label}</option>
            {/each}
          </select>
        </div>

        <div class="form-group">
          <label class="label" for="dev_brand">Marca *</label>
          <input id="dev_brand" name="brand" type="text" class="input" bind:value={deviceForm.brand} required placeholder="Ej: Samsung, Apple..." />
        </div>

        <div class="form-group">
          <label class="label" for="dev_model">Modelo</label>
          <input id="dev_model" name="model" type="text" class="input" bind:value={deviceForm.model} placeholder="Ej: Galaxy S21" />
        </div>

        <div class="form-group">
          <label class="label" for="dev_serial">Nº de Serie / IMEI</label>
          <input id="dev_serial" name="serial_number" type="text" class="input" bind:value={deviceForm.serial_number} placeholder="Opcional" />
        </div>

        <div class="form-group">
          <label class="label" for="dev_color">Color</label>
          <input id="dev_color" name="color" type="text" class="input" bind:value={deviceForm.color} placeholder="Ej: Negro" />
        </div>

        <div class="form-group">
          <label class="label" for="dev_storage">Almacenamiento</label>
          <input id="dev_storage" name="storage" type="text" class="input" bind:value={deviceForm.storage} placeholder="Ej: 128GB" />
        </div>

        <div class="form-group">
          <label class="label" for="dev_pass">Patrón/Contraseña</label>
          <input id="dev_pass" name="password_pattern" type="text" class="input" bind:value={deviceForm.password_pattern} placeholder="PIN, patrón..." />
        </div>

        <div class="form-group">
          <label class="label" for="dev_acc">Accesorios</label>
          <input id="dev_acc" name="accessories" type="text" class="input" bind:value={deviceForm.accessories} placeholder="Cargador, funda..." />
        </div>
      </div>

      {#if showDescription}
      <div class="form-group full-width">
        <label class="label" for="dev_desc">Descripción del problema / Trabajo a realizar *</label>
        <textarea id="dev_desc" name="description" class="textarea" bind:value={deviceForm.description} placeholder="Describa el problema..." rows="3"></textarea>
      </div>
      {/if}
    </div>
  </div>

  <div class="custom-modal-footer">
    {#if onClose}
    <button type="button" class="btn btn-outline" on:click={onClose}>Cancelar</button>
    {/if}
    <button type="submit" class="btn btn-primary">
      {submitLabel}
    </button>
  </div>
</form>

<!-- Modal Cámara -->
{#if showCamera}
<div class="camera-overlay" on:click|self={closeCamera} on:keydown={(e) => e.key === 'Escape' && closeCamera()} role="button" tabindex="0">
  <div class="camera-modal">
    <div class="camera-header">
      <h3>{cameraMode === 'photo' ? 'Tomar Foto' : 'Grabar Video'}</h3>
      <button class="camera-close" type="button" on:click={closeCamera}>×</button>
    </div>
    <div class="camera-body">
      <video bind:this={videoElement} autoplay playsinline>
        <track kind="captions" />
      </video>
      <div class="camera-controls">
        {#if cameraMode === 'photo'}
        <button class="btn btn-primary btn-lg" type="button" on:click={takePhoto}>
          📷 Capturar Foto
        </button>
        {:else}
        <button class="btn {isRecording ? 'btn-danger' : 'btn-primary'} btn-lg" type="button" on:click={toggleRecording}>
          {isRecording ? '⏹ Detener' : '⏺ Grabar'}
        </button>
        {/if}
      </div>
      {#if cameraMode === 'video' && isRecording}
      <p class="recording-indicator">
        <span class="recording-dot"></span> Grabando... (máx 30s)
      </p>
      {/if}
    </div>
  </div>
</div>
{/if}

<style>
  .custom-modal-body {
    padding: 0;
  }

  .form-section {
    padding: 1.25rem;
    border-bottom: 1px solid var(--border);
  }

  .form-section:last-child {
    border-bottom: none;
  }

  .section-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1rem;
    font-weight: 600;
    color: var(--dark);
    margin-bottom: 1rem;
  }

  .section-title svg {
    width: 20px;
    height: 20px;
    color: var(--primary);
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-group.full-width {
    grid-column: 1 / -1;
  }

  .label {
    display: block;
    margin-bottom: 0.375rem;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text);
  }

  .select, .input, .textarea {
    width: 100%;
    padding: 0.625rem 0.875rem;
    font-size: 0.875rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    background: white;
    color: var(--text);
  }

  .select:focus, .input:focus, .textarea:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  }

  .textarea {
    resize: vertical;
    min-height: 80px;
    font-family: inherit;
  }

  .photo-actions {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
  }

  .photos-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 0.5rem;
  }

  .photo-item {
    position: relative;
    aspect-ratio: 1;
    border-radius: var(--radius);
    overflow: hidden;
    background: var(--light);
  }

  .photo-item img, .photo-item video {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .remove-photo {
    position: absolute;
    top: 4px;
    right: 4px;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: rgba(239, 68, 68, 0.9);
    color: white;
    border: none;
    font-size: 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1;
  }

  .text-muted {
    color: var(--text-light);
    font-size: 0.875rem;
  }

  .text-sm {
    font-size: 0.8125rem;
  }

  .custom-modal-footer {
    padding: 1.25rem;
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    background: white;
  }

  /* Cámara */
  .camera-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .camera-modal {
    background: white;
    border-radius: var(--radius-lg);
    max-width: 600px;
    width: 90%;
    overflow: hidden;
  }

  .camera-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid var(--border);
  }

  .camera-header h3 {
    margin: 0;
    font-size: 1.125rem;
  }

  .camera-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: var(--text-light);
    padding: 0.25rem;
    line-height: 1;
  }

  .camera-body {
    padding: 1rem;
  }

  .camera-body video {
    width: 100%;
    border-radius: var(--radius);
    background: #000;
  }

  .camera-controls {
    display: flex;
    justify-content: center;
    margin-top: 1rem;
    gap: 1rem;
  }

  .recording-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 0.75rem;
    color: var(--danger);
    font-size: 0.875rem;
  }

  .recording-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--danger);
    animation: pulse 1s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  @media (max-width: 640px) {
    .form-grid {
      grid-template-columns: 1fr;
    }

    .photo-actions {
      flex-direction: column;
    }

    .photo-actions .btn {
      width: 100%;
    }

    .photos-grid {
      grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    }
  }
</style>
