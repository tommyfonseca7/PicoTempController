class WebServer:
    def web_page(self, T_in, H_in, T_out, H_out, timestamp):
        try:
            with open("index.html", 'r') as file:
                html = file.read()
            return html
        except Exception as e:
            print(f"Error reading index.html: {e}")
            return "Error loading page"

    def parse_query_string(self, qs):
        parameters = {}
        ampersandSplit = qs.split("&")
        for element in ampersandSplit:
            equalSplit = element.split("=")
            parameters[equalSplit[0]] = equalSplit[1]
        return parameters

    def parse_http_request(self, req_buffer):
        assert (req_buffer != b''), 'Empty request buffer.'
        req = {}    
        req_buffer_lines = req_buffer.decode('utf8').split('\r\n')
        req['method'], target, req['http_version'] = req_buffer_lines[0].split(' ', 2)  # Example: GET /route/path HTTP/1.1
        
        print(f"HTTP request target: {target}")
        
        if '?' not in target:
            req['path'] = target
            req['query'] = {}
        else:  # target can have a query component, so /route/path could be something like /route/path?state=on&timeout=30
            req['path'], query_string = target.split('?', 1)
            req['query'] = self.parse_query_string(query_string)

        req['headers'] = {}
        for i in range(1, len(req_buffer_lines) - 1):
            if req_buffer_lines[i] == '':  # Blank line signifies the end of headers.
                break
            else:
                name, value = req_buffer_lines[i].split(':', 1)
                req['headers'][name.strip()] = value.strip()

        req['body'] = req_buffer_lines[-1]  # Last line is the body (or blank if no body.)
            
        return req
