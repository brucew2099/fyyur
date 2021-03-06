window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

function deleteArtist (e, id) {
  e.preventDefault();
  console.log('event', e);

  fetch('/artists/' + id, {
      method: 'DELETE'
  }).then(response => {
    if (response.redirected) {
        window.location.href = response.url;
    }
})
};

function deleteVenue (e, id) {
  e.preventDefault();
  console.log('event', e);

  fetch('/venues/' + id, {
      method: 'DELETE'
  }).then(response => {
    if (response.redirected) {
        window.location.href = response.url;
    }
})
};
