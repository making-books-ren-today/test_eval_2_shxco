module.exports = {
    ci: {
        collect: {
            url: [
                'http://localhost:8000/',
                'http://localhost:8000/members',
                'http://localhost:8000/books',
                'http://localhost:8000/analysis',
                'http://localhost:8000/sources',
                'http://localhost:8000/about',
            ],
            startServerCommand: 'python manage.py runserver --insecure',
            startServerReadyPattern: 'Quit the server with CONTROL-C.'
        },
        upload: {
            target: 'temporary-public-storage',
        },
    },
};