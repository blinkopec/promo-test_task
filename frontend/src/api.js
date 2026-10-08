function getCookie(name) {
    const cookies = document.cookie.split('; ');
    for (const cookie of cookies) {
        const [key, value] = cookie.split('=')
        if (key == name) return decodeURIComponent(value);
   }
   return null
}

export async function apiFetch(url, options = {}) {
    const opts = {
        ...options,
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            ...(options.headers || {}),
        },
    }; 

    if (opts.method && opts.method !== 'GET') {
        const csrf = getCookie('csrftoken');

        if (csrf) {
            opts.headers['X-CSRFToken'] = csrf;
        }
    }

    const result = await fetch(url, opts);

    let data = null;
    try {
        data = await result.json();
    } catch (_) {

    }

    return {
        ok: result.ok,
        status: result.status,
        data,
    };

}