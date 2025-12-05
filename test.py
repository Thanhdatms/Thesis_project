# import re
# import json

# def chunk_txt_to_json(path_txt, output_path):
#     # Đọc file
#     with open(path_txt, "r", encoding="utf-8") as f:
#         text = f.read()

#     # Chỉ lấy từ "CHƯƠNG I" trở đi
#     match = re.search(r'CHƯƠNG\s+I', text, re.IGNORECASE)
#     if not match:
#         return []
#     text = text[match.start():]

#     # Regex tìm mục con: 1.1, 1.2, 1.3, …
#     pattern = r'(\d+\.\d+)\.?\s+(.+?)\n'
#     matches = list(re.finditer(pattern, text, re.DOTALL))

#     results = []

#     for i, m in enumerate(matches):
#         muc = m.group(1)
#         title = m.group(2).strip()

#         # Xác định đoạn nội dung
#         start = m.end()
#         end = matches[i+1].start() if i + 1 < len(matches) else len(text)
#         content = text[start:end].strip()

#         # Lấy số chương theo số trước dấu chấm
#         chuong = int(muc.split('.')[0])

#         results.append({
#             "chương": chuong,
#             "mục": muc,
#             "tiêu đề": title,
#             "nội dung": content
#         })

#     # ---- LƯU RA FILE JSON ----
#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(results, f, indent=2, ensure_ascii=False)

#     return results


# # Ví dụ sử dụng:
# path_input = "So_tay_nhan_vien.txt"
# path_output = "ouput.json"

# chunk_txt_to_json(path_input, path_output)

# print("Đã lưu file JSON tại:", path_output)


import re
import json

def chunk_txt_to_json(path_txt, output_path):
# ---- Đọc file ----
with open(path_txt, "r", encoding="utf-8") as f:
text = f.read()

```
# ---- Chỉ lấy từ "CHƯƠNG I" trở đi ----
match = re.search(r'CHƯƠNG\s+I', text, re.IGNORECASE)
if not match:
    return []
text = text[match.start():]

# ---- Chuẩn hóa xuống dòng: loại bỏ nhiều khoảng trắng thừa ----
text = re.sub(r'\r\n', '\n', text)
text = re.sub(r'[ \t]+', ' ', text)

# ---- Regex tìm mục con (1.1, 1.2, …) ----
# Giới hạn chương thực tế: 1-99 (có thể điều chỉnh nếu file có nhiều hơn)
pattern = r'^(\d{1,2}\.\d+)\.?\s+([^\n]+)'
matches = list(re.finditer(pattern, text, re.MULTILINE))

results = []

for i, m in enumerate(matches):
    muc = m.group(1)
    title = m.group(2).strip()

    # ---- Xác định đoạn nội dung cho mỗi mục ----
    start = m.end()
    end = matches[i+1].start() if i + 1 < len(matches) else len(text)
    content = text[start:end].strip()

    # ---- Lấy số chương theo số trước dấu chấm ----
    chuong = int(muc.split('.')[0])

    results.append({
        "chương": chuong,
        "mục": muc,
        "tiêu đề": title,
        "nội dung": content
    })

# ---- LƯU RA FILE JSON ----
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

return results


# ---- Ví dụ sử dụng ----

path_input = "So_tay_nhan_vien.txt"
path_output = "output.json"

chunk_txt_to_json(path_input, path_output)
print("Đã lưu file JSON tại:", path_output)
