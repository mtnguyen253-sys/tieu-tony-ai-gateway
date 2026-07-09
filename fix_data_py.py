with open("src/data.ts", "r") as f:
    content = f.read()

content = content.replace(
    "    desc: 'Điểm bắt đầu thực thi chương trình. Nạp cấu hình và in thông báo khởi động \"Gateway started\".'\n  }\n  'ai_gateway/registry/capability.py': {",
    "    desc: 'Điểm bắt đầu thực thi chương trình. Nạp cấu hình và in thông báo khởi động \"Gateway started\".'\n  },\n  'ai_gateway/registry/capability.py': {"
)

with open("src/data.ts", "w") as f:
    f.write(content)
