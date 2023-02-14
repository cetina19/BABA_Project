const btn = document.getElementById('Hide_Show');

            btn.addEventListener('click', () => {
            const form = document.getElementById('Upload');

            if (form.style.display === 'none') {
                form.style.display = 'block';
                } else {
                form.style.display = 'none';
                }
            });