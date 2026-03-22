<script>
  import ReceptionModal from './ReceptionModal.svelte';
  import DeviceDetailModal from './DeviceDetailModal.svelte';
  import PhotoGallery from './PhotoGallery.svelte';
  import TicketModal from '../common/TicketModal.svelte';
  import StatusModal from '../common/StatusModal.svelte';

  import { activeModal, modalContext, closeModal, openModal } from '../../stores/modals.js';

  export let customers = [];
  export let onSuccessReception = async () => {};
  export let onPrintTicket = (data) => {};
  export let selectedDeviceRepairs = [];
  export let deviceStatusLabels = {};
  export let handleStatusSelect = async (status) => {};
</script>

<!-- POS Modal Host: Renders at the very top level to avoid Z-index & stacking issues -->
<div class="pos-modal-host">
  {#if $activeModal === 'reception'}
    <ReceptionModal 
      show={true} 
      {customers} 
      onClose={closeModal} 
      onSuccess={async () => { closeModal(); await onSuccessReception(); }} 
      onPrintTicket={(data) => { onPrintTicket(data); openModal('ticket', { ticketData: data }); }} 
    />
  {/if}

  {#if $activeModal === 'detail' && $modalContext?.device}
    <DeviceDetailModal
      show={true}
      device={$modalContext.device}
      customer={$modalContext.device?.customer}
      repairs={selectedDeviceRepairs}
      onClose={closeModal}
      onStatusChange={() => { 
        // Need to chain modals? Or handle inside POS
      }}
      onEdit={() => {}}
    />
  {/if}

  {#if $activeModal === 'gallery' && $modalContext?.photos}
    <PhotoGallery 
      show={true} 
      photos={$modalContext.photos} 
      currentIndex={$modalContext.currentIndex || 0} 
      onClose={closeModal} 
    />
  {/if}

  {#if $activeModal === 'ticket' && $modalContext?.ticketData}
    <TicketModal 
      show={true} 
      ticketData={$modalContext.ticketData} 
      onClose={closeModal} 
    />
  {/if}

  {#if $activeModal === 'status' && $modalContext?.device}
    <StatusModal 
      show={true} 
      options={deviceStatusLabels} 
      onSelect={handleStatusSelect} 
      onClose={closeModal} 
    />
  {/if}
</div>

<style>
  /* Force global override just in case */
  :global(.pos-modal-host .modal-overlay),
  :global(.modal-overlay) { 
    z-index: 100000 !important; 
    opacity: 1 !important; 
    visibility: visible !important; 
    display: flex !important;
  }
</style>
