import pymem

process_name = "MuMuVMMHeadless.exe"
pm = pymem.Pymem(process_name)

# data = pm.read_double(0x778071B89A9C)
# print(data)

pattern = b"\x00\x00\x00\x00\x40\x00\xD9\x40"
PATTERN = "90 33 01 04 00 00 00 00 ?? ?? ?? ?? 05 00 00 00 05 00 00 00 00 00 80 3F"
results = pm.pattern_scan_all(pattern, return_multiple=True)
print(results)

# for result in results:
#     result = result - 16
#     data = pm.read_double(result)
#     if data == 237.0:
#         print(hex(result), data)
#         sun = data
#         believer = pm.read_double(result - 15 * 8)
#         star = pm.read_double(result - 35 * 8)
#         print(f"日光数量为:  {sun}\n信徒数量为:  {believer}\n星光数量为:  {star}")
