from keras.engine import Model
from keras.layers import Input, Flatten, Dense, Conv2D,SpatialDropout2D

from Layers.layer_wrappers.on_list_wrappers import *
from utils.opt_utils import get_filter_size,get_gate_activation
from keras.regularizers import l1,l2
from keras.layers.merge import add,concatenate
import numpy as np
layer_index=0
def get_layer_index():
	global layer_index
	layer_index=layer_index+1
	return layer_index
def model_constructor(layer_sequence,opts,nb_classes,input_shape,nb_filter_list=None,filter_size_list = None,
                      model_dict=None):
	'nb_filter_list is total filters used in each layer.filter size is for convolution'

	img_input = Input(shape=input_shape, name='image_batch')
	x = [img_input]
	expand_rate = opts['model_opts']['param_dict']['param_expand']['rate']
	layer_index_t = 0
	filter_size_index =0
	conv_nb_filterindex=0
	branch = 1
	batch_norm = False
	fully_drop =0
	leak_rate=0
	child_probability=.5
	counter = False # for prelu permutation
	flatten_flag = False
	no_class_dense=False
	for layer in model_dict:
		w_regularizer_str = opts['model_opts']['param_dict']['w_regularizer']['method']
		if w_regularizer_str == 'l1':
			w_reg = l1(opts['model_opts']['param_dict']['w_regularizer']['value'])
			b_reg = l1(opts['model_opts']['param_dict']['w_regularizer']['value'])
		if w_regularizer_str == None:
			w_reg = None
			b_reg = None
		if w_regularizer_str == 'l2':
			w_reg = l2(opts['model_opts']['param_dict']['w_regularizer']['value'])
			b_reg = l2(opts['model_opts']['param_dict']['w_regularizer']['value'])
		component = layer['type']
		if layer['type'] not in ['e','s','rm','am','mp','ma','rbe','d']:
			assert 'Invalid Layer'

		if not layer_index_t == 0:
			input_shape = (None,None,None)
		# if nb_filter_list is not None and component in ['e','s','rm','am','rbe','rbs']:
		# 	nb_filter=nb_filter_list[conv_nb_filterindex]
		# if filter_size_list is not None:
		# 	f_size = filter_size_list[filter_size_index]
		param =layer['param']
		with tf.name_scope(component) as scope:
			if component =='besh':
				#binary expand shared
				nb_filter = param['f']
				f_size = int(param['r'])
				if param.has_key('p'):
					dropout = param['p']
				stride=1
				# x = conv_relu_on_list(input_tensor_list=x, nb_filter=int(nb_filter * expand_rate / branch),
				#                               filter_size=f_size, input_shape=input_shape, w_reg=w_reg,
				#                               gate_activation=get_gate_activation(opts), layer_index=layer_index_t,
				#                               border_mode='same',stride=stride,b_reg= b_reg)
				conv_layer_to_pass = Conv2D(int(nb_filter*expand_rate), (f_size, f_size), activation=None,
				                                   input_shape=input_shape, padding='same', kernel_regularizer=w_reg,
				                                  name='CONV_L'+str(layer_index_t))
				x = conv_birelu_expand_on_list_shared(input_tensor_list=x,
				                               gate_activation=get_gate_activation(opts), layer_index=layer_index_t,batch_norm=0,
				                               leak_rate=0,child_p = 0,conv_layer=conv_layer_to_pass,drop_path_rate
				                                      = dropout)
			if component =='beshpermute':
				#the output tensors would be 2^(n+C) if we have n input tensors and C as kernel channels
				nb_filter = param['f']
				f_size = int(param['r'])
				if param.has_key('p'):
					dropout = param['p']
				if param.has_key('rand'):
					random_permute_flag = int(param['rand'])
				max_perm = 2
				if param.has_key('max_perm'):
					max_perm = int(param['max_perm'])

				conv_layer_to_pass = Conv2D(int(nb_filter*expand_rate), (f_size, f_size), activation=None,
				                                   input_shape=input_shape, padding='same', kernel_regularizer=w_reg,
				                                  name='CONV_L'+str(layer_index_t))
				x = conv_birelu_expand_on_list_shared_permute_channels(input_tensor_list=x,
				                               gate_activation=get_gate_activation(opts), layer_index=layer_index_t,batch_norm=0,
				                               leak_rate=0,child_p = 0,conv_layer=conv_layer_to_pass,drop_path_rate
				                                      = dropout,max_perm=max_perm,random_permute_flag=random_permute_flag)
			if component =='shdense':
				max = 0
				if param.has_key('m'):
					max = float(param['m'])
				n = int(param['n'])
				if n==-1:
					n = nb_classes
				d = param['do']
				x = node_list_to_list(x)
				flatten_flag = True
				dense = Dense(n)
				res  = []
				for tensor in x:
					tensor_f = Flatten()(tensor)
					if not d ==0:
						tensor_f = Dropout(d)(tensor_f)
					tensor_f = dense(tensor_f)
					res+=[tensor_f]
				if res.__len__()==1:
					res_sum = res[0]
				else:
					res_sum = add(res)
				if max==0:
					x= res_sum
				else:
					res_max = MaxoutDenseOverParallel()(res)
					x = res_max
					if max ==.5:
						x = add([res_max,res_sum])
				x = Activation('softmax')(x)
			if component =='shdense_legacy':
				max = 0
				if param.has_key('m'):
					max = float(param['m'])
				n = int(param['n'])
				if n==-1:
					n = nb_classes
				d = param['do']
				x = node_list_to_list(x)
				flatten_flag = True
				dense = Dense(n)
				res  = []
				for tensor in x:
					tensor_f = Flatten()(tensor)
					if not d ==0:
						tensor_f = Dropout(d)(tensor_f)
					tensor_f = dense(tensor_f)
					res+=[tensor_f]

				res_sum = add(res)
				if max==0:
					x= res_sum
				else:
					# res = K.expand_dims()
					res_max = MaxoutDenseOverParallel()(res)
					x = res_max
					if max ==.5:
						x = add([res_max,res_sum])
			if component == 'shdensedoi':
				# dropout instanse
				# tdo is tensor dropout which is the usuall dropout
				# ido is instance dropout
				max = 0
				if param.has_key('m'):
					max = float(param['m'])
				n = int(param['n'])
				if n == -1:
					n = nb_classes
				dense_dropout = float(param['tdo'])
				classification_dropout = float(param['ido'])
				x = node_list_to_list(x)
				if classification_dropout ==-1:
					classification_dropout = .75
				flatten_flag = True
				dense = Dense(n)
				res = []
				for tensor in x:
					tensor_f = Flatten()(tensor)
					if not dense_dropout == 0:
						tensor_f = Dropout(dense_dropout)(tensor_f)
					tensor_f = dense(tensor_f)
					tensor_f = InstanceDropout(classification_dropout)(tensor_f)
					res += [tensor_f]
				res_sum = add(res)
				if max == 0:
					x = res_sum
				else:
					# res = K.expand_dims()
					res_max = MaxoutDenseOverParallel()(res)
					x = add([res_max, res_sum])
			if component == 'mp':
				f_size = param['r']
				strides = int(2)
				x = max_pool_on_list(input_tensor_list=x, strides=(strides, strides), layer_index=layer_index_t,
				                     pool_size=f_size)
				conv_nb_filterindex-=1
			if component=='ap':
				f_size = int(param['r'])
				x =avg_pool_on_list(input_tensor_list=x,strides=(2,2),layer_index=layer_index_t,
				                    pool_size=f_size)
				conv_nb_filterindex-=1
			#TODO Create a general dropout later. its not complete yet.remove todo after complete
			if component=='gdropout':
				# general dropout layer including instance dropout and 2d dropout
				dense_dropout = float(param['tdo'])
				classification_dropout = float(param['ido'])
				for tensor in x:
					tensor_f = Flatten()(tensor)
					if not dense_dropout == 0:
						tensor_f = Dropout(dense_dropout)(tensor_f)
					tensor_f = dense(tensor_f)
					tensor_f = InstanceDropout(classification_dropout)(tensor_f)
					res += [tensor_f]
				res_sum = add(res)
			if component=='leaffully':
				if param.has_key('n'):
					n = param['n']
				else:
					n = 0
				x = node_list_to_list(x)
				if param.has_key('chw'):
					if param['chw']==1:
						x = FullyConnectedTensors(int(n),shared_axes=[2,3])(x)
				else:
					x = FullyConnectedTensors(int(n))(x)
			if component=='cr':
				nb_filter = param['f']
				f_size = int(param['r'])
				conv_layer_to_pass = Conv2D(int(nb_filter * expand_rate), (f_size, f_size), activation=None,
				                                   input_shape=input_shape, padding='same', kernel_regularizer=w_reg,
				                                    name='CONV_L'+str(layer_index_t))(x[0])
				tensors = Birelu('relu',name='BER_CR')(conv_layer_to_pass)
				x = [concatenate(tensors,axis=1)]
			if component=='e':
				nb_filter = param['f']
				f_size = param['r']
				x = conv_birelu_expand_on_list(input_tensor_list=x,nb_filter=int(nb_filter * expand_rate/branch),
				                               filter_size=f_size,
		                               input_shape=input_shape, w_reg=w_reg,
		                       gate_activation=get_gate_activation(opts), layer_index=layer_index_t,border_mode='same')
				branch=2*branch
			if component =='rsh':
				#binary expand shared
				nb_filter = param['f']
				f_size = param['r']
				if param.has_key('p'):
					dropout = param['p']

				conv_layer_to_pass = Conv2D(int(nb_filter*expand_rate), f_size, f_size, activation=None,
				                                   input_shape=input_shape, padding='same', kernel_regularizer=w_reg,
				                                  )
				x = conv_relu_expand_on_list_shared(input_tensor_list=x,
				                               gate_activation=get_gate_activation(opts), layer_index=layer_index_t,batch_norm=0,
				                               leak_rate=0,child_p = 0,conv_layer=conv_layer_to_pass,drop_path_rate
				                                      = dropout)
			if component == 'cshfixedfilter':
				#expand rate does not affect num of filter for this convolution
				nb_filter = param['f']
				f_size = param['r']
				conv_to_pass = Conv2D(int(nb_filter), f_size, f_size,
				 activation = None, input_shape = input_shape, padding = 'same', W_regularizer = w_reg,
				)
				x= node_list_to_list(x)
				for i in range(x.__len__()):
					x[i]= conv_to_pass(x[i])
			if component == 'xaesh':
				# binary expand shared
				nb_filter = param['f']
				f_size = param['r']
				if param.has_key('p'):
					dropout = param['p']
				conv_layer_to_pass = Conv2D(int(nb_filter * expand_rate), f_size, f_size, activation=None,
				                                   input_shape=input_shape, padding='same', kernel_regularizer=w_reg, )
				x = conv_xavr_expand_on_list_shared(input_tensor_list=x, gate_activation=get_gate_activation(opts),
				                                      layer_index=layer_index_t, batch_norm=0, leak_rate=0, child_p=0,
				                                      conv_layer=conv_layer_to_pass, drop_path_rate=dropout)
			if component == 'xaresh':
				# binary expand shared
				nb_filter = param['f']
				f_size = param['r']
				if param.has_key('p'):
					dropout = param['p']
				conv_layer_to_pass = Conv2D(int(nb_filter * expand_rate), f_size, f_size, activation=None,
				                                   input_shape=input_shape, padding='same', kernel_regularizer=w_reg, )
				x = conv_xavrrelu_expand_on_list_shared(input_tensor_list=x, gate_activation=get_gate_activation(opts),
				                                      layer_index=layer_index_t, batch_norm=0, leak_rate=0, child_p=0,
				                                      conv_layer=conv_layer_to_pass, drop_path_rate=dropout)
			if component == 'rbe':
				if param.has_key('p'):
					dropout = param['p']
				if param.has_key('leak'):
					leak_rate = param['leak']
				if param.has_key('bn'):
					batch_norm = param['bn']
				if param.has_key('cp'):
					child_probability = param['cp']
				nb_filter = param['f']
				f_size = param['r']

				x = conv_birelu_expand_on_list(input_tensor_list=x, nb_filter=int(nb_filter * expand_rate / branch),
				                               filter_size=f_size, input_shape=input_shape, w_reg=w_reg,
				                               gate_activation=get_gate_activation(opts), layer_index=layer_index_t,
				                               border_mode='same',relu_birelu_switch=dropout,batch_norm=batch_norm,
				                               leak_rate=leak_rate,child_p = child_probability)

				branch = 2 * branch
			if component == 'pre':
				if param.has_key('p'):
					dropout = param['p']
				if param.has_key('bn'):
					batch_norm = param['bn']
				if param.has_key('cp'):
					child_probability = param['cp']
				if param.has_key('counter'):
					if param['counter']==1:
						counter=True
					else:
						counter=False
				nb_filter = param['f']
				f_size = param['r']

				x = conv_prelu_expand_on_list(input_tensor_list=x, nb_filter=int(nb_filter * expand_rate / branch),
				                               filter_size=f_size, input_shape=input_shape, w_reg=w_reg,
				                               gate_activation=get_gate_activation(opts), layer_index=layer_index_t,
				                               border_mode='same', relu_birelu_switch=dropout, batch_norm=batch_norm,
				                               leak_rate=0, child_p=child_probability,prelu_counter=counter)

				branch = 2 * branch
			if component == 'rbeg':
				if param.has_key('p'):
					dropout = param['p']
				if param.has_key('leak'):
					leak_rate = param['leak']
				if param.has_key('bn'):
					batch_norm = param['bn']
				nb_filter = param['f']
				f_size = param['r']

				x = conv_birelu_expand_on_list_general_leak(input_tensor_list=x, nb_filter=int(nb_filter * expand_rate / branch),
				                               filter_size=f_size, input_shape=input_shape, w_reg=w_reg,
				                               gate_activation=get_gate_activation(opts), layer_index=layer_index_t,
				                               border_mode='same',relu_birelu_switch=dropout,batch_norm=batch_norm,
				                               leak_rate=leak_rate)
				branch = 2 * branch
			if component == 'rben':
				if param.has_key('p'):
					dropout = param['p']
				nb_filter = param['f']
				f_size = param['r']
				x = conv_birelunary_expand_on_list(input_tensor_list=x, nb_filter=int(nb_filter * expand_rate / branch),
				                               filter_size=f_size, input_shape=input_shape, w_reg=w_reg,
				                               gate_activation=get_gate_activation(opts), layer_index=layer_index_t,
				                               border_mode='same',relu_birelu_switch=dropout)
				branch = (2**nb_filter) * branch
			if component=='s':
				nb_filter = param['f']
				f_size = param['r']
				x = conv_birelu_swap_on_list(input_tensor_list=x, nb_filter=int(nb_filter * expand_rate/(branch/2)),
				                             filter_size=f_size,
				                               input_shape=input_shape, w_reg=w_reg,
				                               gate_activation=get_gate_activation(opts), layer_index=layer_index_t,
				                               border_mode='same')
			if component=='rbs':
				if param.has_key('p'):
					dropout = param['p']
				nb_filter = param['f']
				f_size = param['r']
				x = conv_birelu_swap_on_list(input_tensor_list=x, nb_filter=int(nb_filter * expand_rate/branch),
				                             filter_size=f_size,
				                               input_shape=input_shape, w_reg=w_reg,
				                               gate_activation=get_gate_activation(opts), layer_index=layer_index_t,
				                               border_mode='same',relu_birelu_switch=dropout)
			if component=='rm':
				nb_filter = param['f']
				branch = branch / 2
				f_size = param['r']
				x = conv_relu_merge_on_list(input_tensor_list=x, nb_filter=int(nb_filter * expand_rate/branch),
				                              filter_size=f_size,
				                               input_shape=input_shape, w_reg=w_reg,
				                               gate_activation=get_gate_activation(opts), layer_index=layer_index_t,
				                               border_mode='same')
			if component=='am':
				nb_filter = param['f']
				branch = branch / 2
				f_size = param['r']
				x = conv_relu_merge_on_list(input_tensor_list=x, nb_filter=int(nb_filter * expand_rate/branch),
				                              filter_size=f_size, input_shape=input_shape, w_reg=w_reg,
				                              gate_activation='avr', layer_index=layer_index_t, border_mode='same')
			if component == 'bm':
				nb_filter = param['f']
				branch = branch / 2
				f_size = param['r']
				x = conv_birelu_merge_on_list(input_tensor_list=x, nb_filter=int(nb_filter * expand_rate / branch),
				                              filter_size=f_size, input_shape=input_shape, w_reg=w_reg,
				                              gate_activation=get_gate_activation(opts), layer_index=layer_index_t,
				                              border_mode='same')

			if component == 'apd':
				f_size = param['r']
				x = avg_pool_on_list(input_tensor_list=x, strides=(1, 1), layer_index=layer_index_t, pool_size=f_size)
				conv_nb_filterindex -= 1
				no_class_dense = True

			if component == 'conv':
				f_size = param['r']
				nb_filter = param['f']
				stride = 1
				if param.has_key('s'):
					stride = param['s']
				border_mode = 'same'
				if param.has_key('b'):
					border_mode = param['b']
					if border_mode == 1:
						border_mode = 'valid'
					else:
						border_mode = 'same'

				x = conv_on_list(input_tensor_list=x, nb_filter=int(nb_filter * expand_rate / branch),
				                      filter_size=f_size, input_shape=input_shape, w_reg=w_reg,
				                      gate_activation=get_gate_activation(opts), layer_index=layer_index_t,
				                      border_mode=border_mode, stride=stride, b_reg=b_reg)
			if component == 'r':
				f_size = int(param['r'])
				nb_filter = int(param['f'])
				stride=1
				if param.has_key('s'):
					stride = int(param['s'])
				border_mode = 'same'
				if param.has_key('b'):
					border_mode = param['b']
					if border_mode ==1:
						border_mode= 'valid'
					else:
						border_mode= 'same'

				x = conv_relu_on_list(input_tensor_list=x, nb_filter=int(nb_filter * expand_rate / branch),
				                              filter_size=f_size, input_shape=input_shape, w_reg=w_reg,
				                              gate_activation=get_gate_activation(opts), layer_index=layer_index_t,
				                              border_mode=border_mode,stride=stride,b_reg= b_reg)
			if component=='d':
				p = param['p']
				x = dropout_on_list(input_tensor_list=x,p=p,layer_index=layer_index_t)
			if component=='c':
				n = param['n']
				branch = branch / 2
				if n == -1:
					while type(x[0])is list:
						x = concat_on_list(input_tensor_list=x, n=1, layer_index=layer_index_t)
				else:
					for i in range(int(n)):
						x = concat_on_list(input_tensor_list=x,n=n,layer_index=layer_index_t)

			if component =='flattensh':
				res = []
				x = node_list_to_list(x)
				flatten_flag = True
				for tensor in x:
					tensor_f = Flatten()(tensor)
					res+=[tensor_f]
					x = res
			if component =='dropoutsh':
				#TODO: remove flatten and dense from this component
				d = param['p']
				x = node_list_to_list(x)
				flatten_flag = True
				res  = []
				for tensor in x:
					tensor_f = Dropout(d)(tensor)
					res+=[tensor_f]
				x = res
			if component =='densesh':
				#TODO:  remove dropout and flatten from densesh .
				n = int(param['n'])
				if param.has_key('act'):
					activation = param['act']
				else:
					activation = None
				if n==-1:
					n = nb_classes
				x = node_list_to_list(x)
				dense = Dense(n,activation=activation)
				res  = []
				for tensor in x:
					tensor = dense(tensor)
					res+=[tensor]
				x= res
			if component == 'merge':
				# TODO:  remove dropout and flatten from densesh .
				if n == -1:
					n = nb_classes
				mode = param['mode']
				x = node_list_to_list(x)
				x = merge(x,mode=mode)
			if component == 'globalpooling':
				max = 0
				if param.has_key('m'):
					max = float(param['m'])
				f_size = param['r']
				x = node_list_to_list(x)
				x = avg_pool_on_list(input_tensor_list=x, strides=(1, 1), layer_index=layer_index_t, pool_size=f_size)
				no_class_dense = True
				flatten_flag = True
				res = []
				for tensor in x:
					tensor_f = Flatten()(tensor)
					res += [tensor_f]
				res_sum = add(res)
				if max == 0:
					x = res_sum
				else:
					# res = K.expand_dims()
					res_max = MaxoutDenseOverParallel()(res)
					x = res_max
					if max == .5:
						x = add([res_max, res_sum])
					x = add([res_max, res_sum])
			if component == 'shdense3':
				max = 0
				if param.has_key('m'):
					max = float(param['m'])
				n = int(param['n'])
				if n == -1:
					n = nb_classes
				dense_dropout = float(param['dode'])
				classification_dropout = float(param['doclas'])
				x = node_list_to_list(x)
				flatten_flag = True
				dense = Dense(n)
				res = []
				for tensor in x:
					tensor_f = Flatten()(tensor)
					if not dense_dropout == 0:
						tensor_f = Dropout(dense_dropout)(tensor_f)
					tensor_f = dense(tensor_f)
					tensor_f = InstanceDropout(classification_dropout)(tensor_f)
					res += [tensor_f]
				res_sum = add(res)
				if max == 0:
					x = res_sum
				else:
					# res = K.expand_dims()
					res_max = MaxoutDenseOverParallel()(res)
					x = res_max
					if max == .5:
						x = add([res_max, res_sum])
					x = add([res_max, res_sum])


			layer_index_t+=1
			conv_nb_filterindex+=1
			filter_size_index+=1

	if not flatten_flag:
		if type(x)==list and (type(x[0]) == list or not x.__len__()==1) :
			x = node_list_to_list(x)
			merged =concatenate(x, axis=1)
		else:
			if type(x)==list:
				x = x[0]
			merged = x
		with tf.name_scope('Flatten'):
			x = Flatten(name='flatten')(merged)
		with tf.name_scope('Dropout'):
			if not fully_drop==0:
				x = Dropout(fully_drop)(x)
		with tf.name_scope('Dense'):
			if not no_class_dense:
				x = Dense(int(nb_classes))(x)
		with tf.name_scope('SoftMax'):
			x = Activation('softmax')(x)
	model = Model(input=img_input, output=x)
	return model
def remove_pooling_from_string(model_string):
	model_string.replace('-ap')

def model_a(opts, input_shape, nb_classes, input_tensor=None, include_top=True, initialization='glorot_normal'):
	if include_top:
		input_shape = input_shape
	else:
		input_shape = (3, None, None)
	if input_tensor is None:
		img_input = Input(shape=input_shape, name='image_batch')
	else:
		img_input = input_tensor

	expand_rate = opts['model_opts']['param_dict']['param_expand']['rate']
	filter_size = get_filter_size(opts)
	if filter_size == -1:
		f_size = [3, 5, 5, 4]
	else:
		f_size = np.min([[32, 16, 7, 3], [filter_size, (filter_size + 1) / 2, filter_size, filter_size - 1]], 0)
	# Layer 1 Conv 5x5 32ch  border 'same' Max Pooling 3x3 stride 2 border valid
	# x = gate_layer_on_list([img_input], int(32 * expand_rate), f_size[0], input_shape=input_shape, opts=opts,
	#                        border_mode='same', merge_flag=False, layer_index=0)
	#nb_filter,filter_size,border_mode,input_shape,w_reg,gate_activation,index,layer_index,
                      #input_tensor_list
	global layer_index
	layer_index=0
	x = conv_birelu_expand_on_list(input_tensor_list=[img_input],nb_filter=int(32 * expand_rate), filter_size=f_size[0],
	                               input_shape=input_shape, w_reg=None,
	                       gate_activation=get_gate_activation(opts), layer_index=get_layer_index(),border_mode='same')
	x = conv_birelu_expand_on_list(input_tensor_list=x,nb_filter=int(32 * expand_rate), filter_size=f_size[0],
	                               input_shape=input_shape, w_reg=None,
	                       gate_activation=get_gate_activation(opts), layer_index=get_layer_index(),border_mode='same')
	x = conv_birelu_expand_on_list(input_tensor_list=x, nb_filter=int(32 * expand_rate), filter_size=f_size[0],
	                               input_shape=input_shape, w_reg=None, gate_activation=get_gate_activation(opts),
	                               layer_index=get_layer_index(), border_mode='same')
	x = conv_birelu_expand_on_list(input_tensor_list=x, nb_filter=int(32 * expand_rate), filter_size=f_size[0],
	                               input_shape=input_shape, w_reg=None, gate_activation=get_gate_activation(opts),
	                               layer_index=get_layer_index(), border_mode='same')
	# x = max_pool_on_list(x, strides=(2, 2), layer_index=get_layer_index())
	x = conv_birelu_swap_on_list(input_tensor_list=x,nb_filter=int(32 * expand_rate), filter_size=f_size[0],
	                               input_shape=input_shape, w_reg=None,
	                       gate_activation=get_gate_activation(opts), layer_index=get_layer_index(),border_mode='same')
	x = conv_birelu_swap_on_list(input_tensor_list=x,nb_filter=int(32 * expand_rate), filter_size=f_size[0],
	                               input_shape=input_shape, w_reg=None,
	                       gate_activation=get_gate_activation(opts), layer_index=get_layer_index(),border_mode='same')
	x = conv_birelu_merge_on_list(input_tensor_list=x,nb_filter=int(32 * expand_rate), filter_size=f_size[0],
	                               input_shape=input_shape, w_reg=None,
	                       gate_activation=get_gate_activation(opts), layer_index=get_layer_index(),border_mode='same')
	# x = max_pool_on_list(x, strides=(2, 2), layer_index=get_layer_index())
	x = conv_birelu_merge_on_list(input_tensor_list=x,nb_filter=int(32 * expand_rate), filter_size=f_size[0],
	                               input_shape=input_shape, w_reg=None,
	                       gate_activation=get_gate_activation(opts), layer_index=get_layer_index(),border_mode='same')
	x = conv_birelu_merge_on_list(input_tensor_list=x, nb_filter=int(32 * expand_rate), filter_size=f_size[0],
	                              input_shape=input_shape, w_reg=None, gate_activation=get_gate_activation(opts),
	                              layer_index=get_layer_index(), border_mode='same')
	x = conv_birelu_merge_on_list(input_tensor_list=x, nb_filter=int(32 * expand_rate), filter_size=f_size[0],
	                              input_shape=input_shape, w_reg=None, gate_activation=get_gate_activation(opts),
	                              layer_index=get_layer_index(), border_mode='same')
	# TODO add stride for conv layer
	# x = maxpool_on_list(x, pool_size=(3, 3), strides=(2, 2),layer_index=1, border_mode='same')
	# #                           Layer 2 Conv 5x5 64ch  border 'same' AveragePooling 3x3 stride 2
	# x = gate_layer_on_list(x, int(64 * expand_rate / 2), f_size[1],
	#                        input_shape=(32, (input_shape[1] - 2), (input_shape[2]) - 2), opts=opts,
	#                        border_mode='same', merge_flag=False, layer_index=2)
	# x = averagepool_on_list(x, pool_size=(3, 3), strides=(2, 2),layer_index=3)
	#
	# #                           Layer 3 Conv 5x5 128ch  border 'same' AveragePooling3x3 stride 2
	# x = gate_layer_on_list(x, int(128 * expand_rate / 4), f_size[2],
	#                        input_shape=(32, (input_shape[1] - 2) / 2, (input_shape[2] - 2) / 2), opts=opts,
	#                        border_mode='same', merge_flag=False,layer_index=4)
	# x = averagepool_on_list(x, pool_size=(3, 3), strides=(2, 2), border_mode='same',layer_index=5)
	# #                           Layer 4 Conv 4x4 64ch  border 'same' no pooling
	# x = gate_layer_on_list(x, int(64 * expand_rate / 8), f_size[3],
	#                        input_shape=(64, ((input_shape[1] - 2) / 2) - 2, ((input_shape[2] - 2) / 2) - 2), opts=opts,
	#                        border_mode='valid', merge_flag=False,layer_index=6)
	# option 1 average pool all x
	# option 2 concat x list into one tensor
	x = node_list_to_list(x)
	merged = x[0]
	if not x.__len__()==1:
		for input1 in x[1:]:
			merged = concatenate([merged, input1],axis=1)
	if not include_top:
		model = Model(input=img_input, output=x)
	else:
		x = Flatten(name='flatten')(merged)
		x = Dense(nb_classes)(x)
		x = Activation('softmax')(x)
		model = Model(input=img_input, output=x)
	return model
def node_list_to_list(array_tensor):
	'convert a hiearchial list to flat list'
	result =[]
	if not type(array_tensor)==list:
		return array_tensor
	else:
		for tensor_list in array_tensor:
			a = node_list_to_list(tensor_list)
			if type(a)==list:
				result+=a
			else:
				result+=[a]
	return result
def parse_model_string(model_string):
	model_string_list = model_string.split('->')
	model_filter_list = []
	nb_filter_list = []
	filter_size_list = []
	expand_dropout= 1
	dict = {}
	result_list = []
	for block in model_string_list:
		filter_dict = {}
		filter = block.split('|')
		filter_name = filter[0]
		filter_dict['type'] = filter_name
		filter_dict['param'] = {}
		parameters = filter[1]
		parameters = parameters.split(',')
		for parameter in parameters:
			param = parameter.split(':')
			param_name = param[0]
			param_val = param[1]
			if not str(param_val).isalpha():
				filter_dict['param'][param_name]=float(param_val)
				if param_name == 'r':
					filter_size_list += [int(param_val)]
				if param_name == 'f':
					nb_filter_list += [int(param_val)]
				if param_name == 'p':
					expand_dropout=float(param_val)
			else:
				filter_dict['param'][param_name] = param_val
		model_filter_list+=[filter_dict]

	return {'filters':model_filter_list,'r_field_size':filter_size_list,'conv_nb_filter':nb_filter_list,
	        'ex_drop':expand_dropout,'dict':model_filter_list}
def get_model(opts, input_shape, nb_classes,model_string,nb_filter_list=None,conv_filter_size_list=None):
	model_dict = parse_model_string(model_string)

	return model_constructor(model_dict['filters'],opts=opts,nb_classes=nb_classes,input_shape=input_shape,
	                         nb_filter_list=model_dict['conv_nb_filter'],filter_size_list=model_dict['r_field_size'],
	                         model_dict = model_dict['dict'])
if __name__ == '__main__':
	model_string = 'rbe|f:32,r:5,p:.75' \
	               '->rbe|f:64,r:5' \
	               '->rbe|f:128,r:5' \
	               '->s|f:128,r:5' \
	               '->mp|s:2,r:3' \
	               '->s|f:256,r:3' \
	               '->ap|s:2,r:3' \
	               '->s|f:512,r:5' \
	               '->ap|s:2,r:3' \
	               '->s|f:256,r:4' \
	               '->ap|s:2,r:3'
	x = parse_model_string(model_string)
	print x