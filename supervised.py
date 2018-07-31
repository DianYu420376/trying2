# coding: utf-8

# In[1]:

'''
Training a fully supervised one layer NMF on 20 news group dataset
'''
# define some global variables
save_PATH = 'saved_data/'
save_filename = 'supervised_one_layer'


# In[2]:

# import package
import torch
from torch.autograd import Variable
import Ipynb_importer
from deep_nmf import Deep_NMF, Energy_Loss_Func, Fro_Norm
from writer import Writer
from matplotlib import pyplot as plt
import numpy as np
from auxillary_functions import *


# In[3]:

# load the dataset for twenty news
from twenty_news_group_data_loading import data, Y, target,L20, L50, L90, sparsedata_cr_entr, sparsedata_L2#, get_whole_output


# In[17]:

# Define the network 
m = data.shape[1]
k = 20
c = 20
lambd = 300
net = Deep_NMF([m, k], c)
loss_func = Energy_Loss_Func(lambd = lambd, classification_type = 'L2')
data_input = data*1000
dataset = sparsedata_L2(data_input, Y)
criterion = Fro_Norm()

# In[18]:

# Training process!

# setting training parameters
batchsize = 100
epoch = 7
lr_nmf = 7000
lr_cl = 5
loss_lst = []
# train!
for epo in range(epoch):
    dataloader = torch.utils.data.DataLoader(dataset, batch_size = batchsize, shuffle = True)
    total_loss = 0
    for (i, (inputs, label)) in enumerate(dataloader):
        inputs = inputs.view([inputs.shape[0], inputs.shape[2]])
        label = label.view([label.shape[0], -1])
        inputs, label = Variable(inputs), Variable(label)
        # train the linear classifier
        S_lst, pred = net(inputs)
        print('training the classifier')
        for k in range(100):
            net.zero_grad()
            pred = net.linear(S_lst[-1].data)
            loss = criterion(pred, label)
            loss.backward()
            #print(loss.data)
            for A in net.linear.parameters():
                A.data = A.data.sub_(lr_cl*A.grad.data)
        # train the lsqnonneg layers
        S_lst,pred = net(inputs)
        net.zero_grad()
        loss = loss_func(inputs, S_lst,list(net.lsqnonneglst.parameters()),pred,label)
        loss.backward()
        loss_lst.append(loss.data)
        total_loss += loss.data
        print('training the nmf layer')
        print(loss.data)
        for A in net.lsqnonneglst.parameters():
            A.data = A.data.sub_(lr_nmf*A.grad.data)
            A.data = A.data.clamp(min = 0)
    print('epoch = ', epo, '\n', total_loss)


# In[19]:

# save the data
np.savez(save_PATH + save_filename,
         param_lst = list(net.parameters()), loss_lst = loss_lst)


# In[20]:

# plot the loss curve
#plt.plot(loss_lst)
#plt.show()
# Get the whole output of the whole dataset (running forward propagation on the whole dataset)
S, pred = get_whole_output(net, dataset)
# Get the accuracy
accuracy = torch.sum(torch.argmax(pred, 1) 
                     == torch.argmax(torch.from_numpy(Y),1))/len(dataset)
print(accuracy)
# Get the reconstruction error
A_np = net.lsqnonneglst[0].A.data.numpy()
S_np = S.data.numpy()
fro_error, fro_X = calc_reconstruction_error(data_input, A_np, S_np)
print(fro_error/fro_X)


# In[ ]:

# save the data
print(S)
print(pred)
np.savez(save_PATH + save_filename, S = S, pred = pred ,
         param_lst = list(net.parameters()), loss_lst = loss_lst)


# In[ ]:



