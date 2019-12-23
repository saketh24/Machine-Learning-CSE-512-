# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10_nY-nCkQCIa-3LmxYiEbZFqUwtPFKJE
"""

import pickle
from google.colab import drive
import pandas as pd
import numpy as np
from sklearn import preprocessing

drive.mount('/content/drive', force_remount = True)

cd '/content/drive/My Drive/MLHW3/'

TrainFileName = 'Train_Features.pkl'
ValFileName = 'Val_Features.pkl'
tr_data = pickle.load(open(TrainFileName,'rb'), encoding='latin1')
val_data = pickle.load(open(ValFileName,'rb'), encoding='latin1')

df1= pd.read_csv('Train_Labels.csv')
df2 = pd.read_csv('Val_Labels.csv')

tr_vec = []
y_train = []
ids = []
val_vec = []
val_y = []
for i,j in zip(df1.Id, df1.Category):
  tr_vec.append(tr_data[i])
  y_train.append(j)
  ids.append(i)
for a,b in zip(df2.Id, df2.Category):
  val_vec.append(val_data[a])
  val_y.append(b)
  
tr_vec = np.array(tr_vec)
y_train = np.array(y_train).reshape(1,4000)
val_y = np.array(val_y).reshape(1,2000)
val_y = val_y[0]
x_bar = np.append(tr_vec,np.ones([len(tr_vec),1]),1)
v_bar = np.append(val_vec, np.ones([len(val_vec),1]),1)
x_bar.shape
v_bar.shape

# scaler = preprocessing.StandardScaler()
# scaler.fit(x_bar)
# x_bar = scaler.transform(x_bar)
x_bar = preprocessing.normalize(x_bar, norm = 'l2')
v_bar = preprocessing.normalize(v_bar, norm = 'l2')
x_bar = x_bar.transpose()
v_bar = v_bar.transpose()

x_bar.shape
v_bar.shape

def logreg(x_bar, y_train, v_bar,val_y, eta0, eta1, m, max_epoch, stop_criteria):
  loss_vals = []
  validation_losses = []
  train_acc = []
  val_acc = []
  theta = np.zeros((x_bar.shape[0],3))
  x = x_bar
  v = v_bar
  y = y_train.reshape((1,4000))
  val_y = val_y.reshape((1,2000))
  for epoch in range(1,max_epoch+1):
    #print(y.shape)
    eta = eta0/(eta1 + epoch)
    i = np.random.permutation(x.shape[1])
    print(x.shape[1])
    x_new = x[:,i]
    y_new = y[:,i]
    print(y_new.shape)    
    
    batches =[]   
    
    n_batches = int(x.shape[1]/m)
    print(str(n_batches) + " is num batches")
    for j in range(0, n_batches):
      x_batch = x_new[:,j*m:(j+1)*m]
      y_batch = y_new[:,j*m:(j+1)*m]
      batches.append((x_batch, y_batch))
    loss_probs = np.zeros((x.shape[1],1))
    val_lp = np.zeros((v.shape[1],1))
    denom = 0
    for n in range(0,x.shape[1]):
      theta_sum = 0
      y_label = int(y_new[0,n])
      for j in range(0,3):
        t = theta[:,j]
        x_n = x_new[:,n]
        t = t.reshape(513,1)
        x_n = x_n.reshape(513,1)
        theta_sum += np.exp(np.dot(t.transpose(),x_n))
      denom = 1 + theta_sum
      if y_label == 4:
        loss_probs[n] = 1/denom
      else:
        loss_probs[n] = (np.exp(np.dot(theta[:,y_label-1].transpose(), x_new[:,n])))/denom
    for n in range(0, v.shape[1]):
      theta_sum = 0
      y_label = int(val_y[0,n])
      for j in range(0,3):
        t = theta[:,j]
        v_n = v[:,n]
        t = t.reshape(513,1)
        v_n = v_n.reshape(513,1)
        theta_sum += np.exp(np.dot(t.transpose(),v_n))
      denom = 1 + theta_sum
      if y_label == 4:
        val_lp[n] = 1/denom
      else:
        val_lp[n] = (np.exp(np.dot(theta[:,y_label-1].transpose(), v[:,n])))/denom
    log_sum = 0
    for i in range(0,x.shape[1]):
      log_sum += np.log(loss_probs[i])
    loss = log_sum * -1/x.shape[1]
    loss_vals.append(loss)
    print(loss)  
    log_val_sum = 0
    for a in range(0,v.shape[1]):
      log_val_sum += np.log(val_lp[a])
    validation_loss = log_val_sum * -1/ v.shape[1]
    validation_losses.append(validation_loss)
    
    #Stochaistic Gradient Descent
    for batch in batches:
      probs = np.zeros((m,4))
      xb_bar = batch[0]
      yb_bar = batch[1]
      for n in range(0,m):
        theta_sum = 0
        y_label = int(yb_bar[0,n])
        for j in range(0,3):
          theta_sum += np.exp(np.dot(theta[:,j].transpose(),xb_bar[:,n]))
        denom = 1 + theta_sum
        for i in range(0,3):
          probs[n,i] = (np.exp(np.dot(theta[:,i].transpose(), xb_bar[:,n])))/denom
        probs[n,3] = 1/denom
      
      for c in range(0,3):
        grad_sum = 0
        delta = 0
        for i in range(0,m):
          if c+1 == yb_bar[:,i]:
            delta = 1
          else:
            delta = 0
          grad = (delta - probs[i,c]) * xb_bar[:,i]
          grad_sum += grad
        gradient = -1 * grad_sum/ m
        theta[:,c] = theta[:,c] - eta*gradient
    for n in range(0,x.shape[1]):
      theta_sum = 0
      y_label = int(y_new[0,n])
      for j in range(0,3):
        theta_sum += np.exp(np.dot(theta[:,j].transpose(),x_new[:,n]))
      denom = 1 + theta_sum
      if y_label == 4:
        loss_probs[n] = 1/denom
      else:
        loss_probs[n] = (np.exp(np.dot(theta[:,y_label-1].transpose(), x_new[:,n])))/denom
    l_sum = 0
    for i in range(0,x.shape[1]):
      l_sum += np.log(loss_probs[i])
    loss_new = l_sum *-1/x.shape[1]
    print("new loss:" + str(loss_new))
    val_loss_probs = []
    tr_loss_probs = []

    
    tr_correct_count = 0
    for i in range(0, x.shape[1]):
      pred_theta_sum = 0 
      pred = 0
      for j in range(0,3):
        pred_theta_sum += np.exp(np.dot(theta[:,j].transpose(),x_new[:,i]))
      denom = 1 + pred_theta_sum
      max_p =0
      for i in range(0,3):
        p = (np.exp(np.dot(theta[:,i].transpose(), x_new[:,i])))/denom
        if p > max_p:
          max_p = p
          pred = i+1
      p_last = 1/denom
      if p_last > max_p:
        pred = 4
      y_label = int(y_new[0,i])
      if y_label == pred:
        tr_correct_count +=1
    train_acc.append(tr_correct_count/x.shape[1])
    print("train acc:" + str(train_acc[-1]))
    
    val_correct_count = 0
    for i in range(0, v.shape[1]):
      pred_theta_sum = 0 
      pred = 0
      for j in range(0,3):
        pred_theta_sum += np.exp(np.dot(theta[:,j].transpose(),v[:,i]))
      denom = 1 + pred_theta_sum
      max_p =0
      for i in range(0,3):
        p = (np.exp(np.dot(theta[:,i].transpose(), v[:,i])))/denom
        if p > max_p:
          max_p = p
          pred = i+1
      p_last = 1/denom
      if p_last > max_p:
        pred = 4
      y_label = int(val_y[0,i])
      if y_label == pred:
        val_correct_count +=1
    val_acc.append(val_correct_count/v.shape[1])
    print("val acc:" + str(val_acc[-1]))
    
    if loss_new> loss and epoch == 1:
      continue
    if loss_new > (1- stop_criteria) * loss:
      loss_vals.append(loss_new)
      validation_losses.append(validation_loss + 0.00001)
      print('Epoch value:' + str(epoch))
      break
  return theta,loss_vals, validation_losses,train_acc,val_acc

theta,loss_vals, validation_losses,train_acc,val_acc = logreg(x_bar,y_train,v_bar, val_y,0.1,1,16,1000,0.00001)

import matplotlib.pyplot as plt
plt.figure()
x = [i for i in range(1,248)]
y = loss_vals
y1 = validation_losses
plt.plot(x,y)
plt.plot(x,y1)
plt.title('Loss Function vs Epoch')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(['Training Loss', 'Validation Loss'], loc='upper left')
plt.show()

plt.figure()
x = [i for i in range(1,247)]
y = train_acc
y1 = val_acc
plt.plot(x,y)
plt.plot(x,y1)
plt.title('Loss Function vs Epoch')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(['Training accuracy', 'Validation accuracy'], loc='upper left')
plt.show()

theta.shape

t_data = pickle.load(open('Test_Features.pkl','rb'), encoding='latin1')

imgs = []
x = []
for key in t_data:
  imgs.append(key)
  x.append(t_data[key])

x = np.array(x)
x=  np.append(x,np.ones([len(x),1]),1).transpose()

x.shape

preds = []

for i in range(0, x.shape[1]):
  pred_theta_sum = 0 
  pred = 0
  for j in range(0,3):
    pred_theta_sum += np.exp(np.dot(theta[:,j].transpose(),x[:,i]))
  denom = 1 + pred_theta_sum
  max_p =0
  for i in range(0,3):
    p = (np.exp(np.dot(theta[:,i].transpose(), x[:,i])))/denom
    if p > max_p:
      max_p = p
      pred = i+1
  p_last = 1/denom
  if p_last > max_p:
    pred = 4
  preds.append(pred)

print(preds)

print(len(preds))

import csv

with open('final_ans.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(zip(imgs, preds))

