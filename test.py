from predict import Predict,vkmodel
from PIL import Image

p=Predict(r'model.pth')
img=Image.open(r'tmp\captcha.png')
c=p.predict(img)
print(c)