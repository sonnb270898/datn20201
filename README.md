# Personal financial management
This is a project we do for the final graduation test



### Requirements
- lanms==1.0.2
- lmdb==1.0.0
- natsort==7.0.1
- nltk==3.4.4
- opencv-contrib-python==4.2.0.34
- torch==1.5.0+cu101
- torchvision==0.6.0+cu101
- flask==1.1.2
- flask-login==0.4.1
- flask-mysql==1.5.1
- transformers==2.11.0
- torchtext==0.6.0



```
pip install -r requirement.txt
```

### Usage

***Weights***

* Create  `src/weights/` to contain weights
* Detection: [here](https://drive.google.com/file/d/1Jk4eGD7crsqCCg9C9VjCLkMN3ze8kutZ/view)
* Recognition: [here](https://drive.google.com/drive/folders/15WPsuPJDCzhp2SvYZLRj8mAlT3zmoAMW)
* Identification: [here](https://drive.google.com/file/d/1-GEm1OKL8gCKHC3Grtg_YltuI_ndrV-V/view?usp=sharing)


***For Running***

More option can find in opt.py

*For test image*

>Edit your image_path and run

```
python handle_img.py --sensitive --checkpoint /path/to/weights/identifier \  
--save_model /path/to/weights/recognizer \
--trained_model /path/to/weights/detection
```

*For run app*

```
python run/app.py --sensitive --checkpoint /path/to/weights/identifier \  
--save_model /path/to/weights/recognizer \
--trained_model /path/to/weights/detection
```

***For Training***

>Please follow the github links below for each stage


***Author***
```
https://github.com/clovaai/CRAFT-pytorch
https://github.com/clovaai/deep-text-recognition-benchmark
https://github.com/wenwenyu/PICK-pytorch
```


