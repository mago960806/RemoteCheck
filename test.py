from remotecheck import map_with_multi_thread_output_json

host_list = [
    [
        '192.168.1.1',
        '22',
        'root',
        'admin123'
    ],
    [
        '192.168.1.2',
        '10022',
        'weblogic',
        'admin123'
    ]
]

result = map_with_multi_thread_output_json(host_list)

print(result)
