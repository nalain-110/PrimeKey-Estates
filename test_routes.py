"""
Comprehensive route tester - tests all routes and reports errors
"""
import sys
import traceback

def test_all():
    from app import create_app
    app = create_app()
    errors = []
    ok = []
    
    with app.app_context():
        with app.test_client() as c:
            # Public routes
            public_routes = [
                ('GET', '/'),
                ('GET', '/properties'),
                ('GET', '/properties/1'),
                ('GET', '/blog'),
                ('GET', '/about'),
                ('GET', '/contact'),
                ('GET', '/agents'),
                ('GET', '/agents/1'),
                ('GET', '/login'),
                ('GET', '/register'),
            ]
            
            for method, url in public_routes:
                try:
                    r = c.open(url, method=method)
                    if r.status_code in [200, 302]:
                        ok.append(f'[OK {r.status_code}] {method} {url}')
                    else:
                        # Try to get error message from response
                        body = r.data.decode('utf-8', errors='replace')
                        # Find error line
                        err_line = ''
                        for line in body.splitlines():
                            if 'Error' in line or 'error' in line or 'Exception' in line or 'Traceback' in line:
                                err_line = line.strip()[:120]
                                break
                        errors.append(f'[ERR {r.status_code}] {method} {url} | {err_line}')
                except Exception as e:
                    errors.append(f'[EXC] {method} {url} | {str(e)[:120]}')
    
    print('\n=== RESULTS ===')
    print(f'PASSED: {len(ok)} | FAILED: {len(errors)}\n')
    for line in ok:
        print(line)
    if errors:
        print('\n--- ERRORS ---')
        for line in errors:
            print(line)
    
    return len(errors) == 0

if __name__ == '__main__':
    sys.exit(0 if test_all() else 1)
