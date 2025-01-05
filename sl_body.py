import basic
import paddlehub as hub


if __name__ == "__main__":  
    handle = basic.get_handle()
    ocr = hub.Module(name="ch_pp-ocrv3", enable_mkldnn=False)       # mkldnn加速仅在CPU下有效
    basic.save_staute(handle, ocr=ocr)
    basic.SL_body(handle, ocr=ocr, star=True)
    basic.save_staute(handle, ocr=ocr)
    
    
    
    