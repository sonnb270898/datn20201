import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt     
from sklearn.metrics import confusion_matrix,accuracy_score
import pylab as pl

_class_name = ['product','price','total','other']

def visual_confusion_matrix(y_true, y_pred, _class_name=_class_name):
    print(accuracy_score(y_true,y_pred))
    cm = confusion_matrix(y_true, y_pred, labels=_class_name)
    print(cm)
    ax= plt.subplot()
    sns.heatmap(cm, annot=True, ax = ax); #annot=True to annotate cells

    # labels, title and ticks
    ax.set_xlabel('Predicted labels');ax.set_ylabel('True labels'); 
    ax.set_title('Confusion Matrix'); 
    ax.xaxis.set_ticklabels(_class_name); ax.yaxis.set_ticklabels(_class_name)
    plt.show()