from datetime import datetime
import io, base64

def current_time() -> str:
    return datetime.now().strftime("%m/%d/%Y")

def get_b64_img(image):       
    bytes_im = io.BytesIO(image)    
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image