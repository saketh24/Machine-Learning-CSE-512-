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
tr_data = pickle.load(open(TrainFileName,'rb'), encoding='latin1')

df1= pd.read_csv('Train_Labels.csv')

tr_vec = []
y_train = []
ids = []
for i,j in zip(df1.Id, df1.Category):
  tr_vec.append(tr_data[i])
  y_train.append(j)
  ids.append(i)
tr_vec = np.array(tr_vec)
y_train = np.array(y_train).reshape(1,4000)
y_train = y_train[0]
x_bar = np.append(tr_vec,np.ones([len(tr_vec),1]),1)

x_bar.shape

# scaler = preprocessing.StandardScaler()
# scaler.fit(x_bar)
# x_bar = scaler.transform(x_bar)
x_bar = preprocessing.normalize(x_bar, norm = 'l2')
x_bar = x_bar.transpose()

x_bar.shape

def logreg(x_bar, y_train, eta0, eta1, m, max_epoch, stop_criteria):
  loss_vals = []
  theta = np.zeros((x_bar.shape[0],3))
  x = x_bar
  y = y_train.reshape((1,4000))
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
    denom = 0
    for n in range(0,x.shape[1]):
      theta_sum = 0
      y_label = int(y_new[0,n])
      for j in range(0,3):
        t = theta[:,j]
        x_n = x_new[:,n]
        t = t.reshape(513,1)
        x_n = x_n.reshape(513,1)
        #print(t.shape)
        #print(x_n.shape)
        theta_sum += np.exp(np.dot(t.transpose(),x_n))
        #print(theta_sum)
      denom = 1 + theta_sum
      if y_label == 4:
        loss_probs[n] = 1/denom
      else:
        loss_probs[n] = (np.exp(np.dot(theta[:,y_label-1].transpose(), x_new[:,n])))/denom
    log_sum = 0
    for i in range(0,x.shape[1]):
      log_sum += np.log(loss_probs[i])
    #loss = np.log(np.sum(loss_probs)) * -1 / x.shape[1]
    loss = log_sum * -1/x.shape[1]
    loss_vals.append(loss)
    print(loss)  
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
          #print(grad.shape)
          grad_sum += grad
        gradient = -1 * grad_sum/ m
        theta[:,c] = theta[:,c] - eta*gradient
        #print(str(gradient) + "is gradient")
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
    #loss_new = np.log(np.sum(loss_probs)) * -1 / x.shape[1]
    loss_new = l_sum *-1/x.shape[1]
    print("new loss:" + str(loss_new))
    if loss_new> loss and epoch == 1:
      continue
    if loss_new > (1- stop_criteria) * loss:
      loss_vals.append(loss_new)
      print('Epoch value:' + str(epoch))
      break
  return theta,loss_vals

theta,loss_vals = logreg(x_bar,y_train,0.1,1,16,1000,0.00001)

import matplotlib.pyplot as plt
plt.figure()
x = [i for i in range(1,248)]
y = loss_vals
plt.plot(x,y)
plt.title('Loss Function vs Epoch')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.show()

print(theta)

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

preds =[]

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

