document.addEventListener('submit', (e)=>{
  const form = e.target.closest('form.advance-status');
  if(!form) return;
  e.preventDefault();
  const fd = new FormData(form);
  fetch(form.action, {method:'POST', body:fd}).then(r=>r.json()).then(data=>{
    if(data.error){ alert(data.error); }
    else{ location.reload(); }
  });
});

