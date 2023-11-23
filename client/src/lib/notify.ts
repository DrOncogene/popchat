import Swal from 'sweetalert2';

const Toast = Swal.mixin({
  toast: true,
  position: 'top-end',
  timer: 5000,
  timerProgressBar: true,
  didOpen: (toast) => {
    toast.onmouseenter = Swal.stopTimer;
    toast.onmouseleave = Swal.resumeTimer;
  },
  background: '#090E0F',
  color: 'white',
  showConfirmButton: true,
  confirmButtonText: 'View',
  confirmButtonColor: '#151B1C'
});

export default Toast;
