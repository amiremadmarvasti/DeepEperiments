from keras.layers import Convolution2D, merge,BatchNormalization,Conv2D
from keras.layers.advanced_activations import PReLU


def conv_relu_expand_shared(conv_layer,gate_activation,index,layer_index,
                      input_tensor,drop_path_rate=1,leak_rate=0,batch_norm=0,child_p=.5):
	"this function is passing data through a convolution and then pass it through the birelu (doubles channels)"
	'returns list'

	data_conv = conv_layer(input_tensor)
	if batch_norm==1:
		data_conv = BatchNormalization(axis=1)(data_conv)
	name = 'RELU_L' + str(layer_index) + '_I' + str(index)
	output_tensor = Relu(activation='relu', name=name)(
		data_conv)
	return output_tensor
def conv_birelu_expand_shared(conv_layer,gate_activation,index,layer_index,
                      input_tensor,drop_path_rate=1,leak_rate=0,batch_norm=0,child_p=.5,random_permute_flag=False):
	"this function is passing data through a convolution and then pass it through the birelu (doubles channels)"
	'returns list'

	data_conv = conv_layer(input_tensor)
	# if batch_norm==1:
	# 	data_conv = BatchNormalization(axis=1)(data_conv)
	name = 'BER_L'+str(layer_index)+'_I'+str(index)
	output_tensor_list = Birelu(gate_activation,relu_birelu_sel=drop_path_rate,name=name,layer_index=layer_index,
	                            leak_rate=leak_rate,child_p=child_p)(data_conv)
	# output_tensor_list = Relu(activation='relu',name=name)
	return output_tensor_list
def conv_birelu_expand_shared_permute_channels(conv_layer,gate_activation,index,layer_index,
                      input_tensor,drop_path_rate=1,leak_rate=0,batch_norm=0,child_p=.5,max_perm =2,
                                               random_permute_flag=False):
	"this function is passing data through a convolution and then pass it through the birelu (doubles channels)"
	'returns list'

	data_conv = conv_layer(input_tensor)
	if batch_norm==1:
		data_conv = BatchNormalization(axis=1)(data_conv)
	name = 'BER_L'+str(layer_index)+'_I'+str(index)
	output_tensor_list = Birelu(gate_activation,relu_birelu_sel=drop_path_rate,name=name,layer_index=layer_index,
	                            leak_rate=leak_rate,child_p=child_p)(
		data_conv)
	with tf.name_scope('Permute') as scope:
		permuted_tensor_list = PermuteChannels(max_perm,random_permute=random_permute_flag)(output_tensor_list)








	return permuted_tensor_list
def conv_xavr_expand_shared(conv_layer,index,layer_index,
                      input_tensor,batch_norm=0):
	"this function is passing data through a convolution and then pass it through the birelu (doubles channels)"
	'returns list'

	data_conv = conv_layer(input_tensor)
	if batch_norm==1:
		data_conv = BatchNormalization(axis=1)(data_conv)

	output_tensor = AVR(name='R_relu_AVR_layer-'+str(
		layer_index)+'_index-'+str(index))(
		data_conv)
	return [output_tensor,data_conv]
def conv_xavrrelu_expand_shared(conv_layer,index,layer_index,
                      input_tensor,batch_norm=0):
	"this function is passing data through a convolution and then pass it through the birelu (doubles channels)"
	'returns list'

	data_conv = conv_layer(input_tensor)
	if batch_norm==1:
		data_conv = BatchNormalization(axis=1)(data_conv)

	output_tensor = AVR(name='R_relu_AVR_layer-'+str(
		layer_index)+'_index-'+str(index))(
		data_conv)
	output_tensor2 = Relu(activation='relu',name='R_relu_layer-'+str(
		layer_index)+'_index-'+str(index))(data_conv)
	return [output_tensor2,output_tensor,data_conv]
def conv_reluavr_expand_shared(conv_layer,index,layer_index,
                      input_tensor,batch_norm=0):
	"this function is passing data through a convolution and then pass it through the birelu (doubles channels)"
	'returns list'

	data_conv = conv_layer(input_tensor)
	if batch_norm==1:
		data_conv = BatchNormalization(axis=1)(data_conv)

	output_tensor = AVR(name='R_relu_AVR_layer-'+str(
		layer_index)+'_index-'+str(index),layer_index=layer_index)(
		data_conv)
	output_tensor2 = Relu('relu',name='R_relu-'+str(
		layer_index)+'_index-'+str(index),layer_index=layer_index)(data_conv)
	return [output_tensor,output_tensor2]

def conv_birelu_expand(nb_filter,filter_size,border_mode,input_shape,w_reg,gate_activation,index,layer_index,
                      input_tensor,relu_birelu_switch=1,leak_rate=0,batch_norm=0,child_p=.5):
	"this function is passing data through a convolution and then pass it through the birelu (doubles channels)"
	'returns list'
	conv_name = 'E_conv_exp_'+'nbfilter-'+str(nb_filter)+'_layer'+str(layer_index)+'_index-'+str(index)
	data_conv = Convolution2D(nb_filter, filter_size, filter_size, activation=None,
	                          input_shape=input_shape, border_mode=border_mode, W_regularizer=w_reg,
	                          name=conv_name)(
		input_tensor)
	if batch_norm==1:
		data_conv = BatchNormalization(axis=1)(data_conv)
	output_tensor_list = Birelu(gate_activation,relu_birelu_sel=relu_birelu_switch,name='E_Birelu_layer-'+str(
		layer_index)+'_index-'+str(index),layer_index=layer_index,leak_rate=leak_rate,child_p=child_p)(
		data_conv)
	return output_tensor_list
def conv_prelu_expand(nb_filter,filter_size,border_mode,input_shape,w_reg,gate_activation,index,layer_index,
                      input_tensor,relu_birelu_switch=1,leak_rate=0,batch_norm=0,child_p=.5,prelu_counter=False):
	"this function is passing data through a convolution and then pass it through the birelu (doubles channels)"
	'returns list'

	data_conv = Convolution2D(nb_filter, filter_size, filter_size, activation=None,
	                          input_shape=input_shape, border_mode=border_mode, W_regularizer=w_reg,
	                          name='E_conv_exp_'+'nbfilter-'+str(nb_filter)+'_layer'+str(layer_index)+'_index-'+str(
		                          index))(
		input_tensor)
	if batch_norm==1:
		data_conv = BatchNormalization(axis=1)(data_conv)


	output_tensor_list = Duplicator(relu_birelu_sel=relu_birelu_switch,child_p=child_p)(data_conv)

	a = PReLU(shared_axes=[1,2, 3], name='PRelu0_' + 'nbfilter-' + str(nb_filter) + '_layer' + str(
	layer_index) + '_index-' + str(index))(output_tensor_list[0])
	b = PReLU(shared_axes=[1,2, 3], name='PRelu1_' + 'nbfilter-' + str(nb_filter) + '_layer' + str(
		layer_index) + '_index-' + str(index))(output_tensor_list[1])
	if prelu_counter:
		output_tensor_list[1]=input_tensor
	return [a,b]
def conv_birelunary_expand(nb_filter,filter_size,border_mode,input_shape,w_reg,gate_activation,index,layer_index,
                      input_tensor,relu_birelu_switch=1):
	"this function is passing data through a convolution and then pass it through the birelu (doubles channels)"
	'returns list'
	data_conv = Convolution2D(nb_filter, filter_size, filter_size, activation=None,
	                          input_shape=input_shape, border_mode=border_mode, W_regularizer=w_reg,
	                          name='E_conv_exp_'+'nbfilter-'+str(nb_filter)+'_layer'+str(layer_index)+'_index-'+str(
		                          index))(
		input_tensor)
	output_tensor_list = Birelu_nary(gate_activation,relu_birelu_sel=relu_birelu_switch,name='E_Birelunary_layer-'+str(
		layer_index)+'_index-'+str(index),layer_index=layer_index,nb_filter=nb_filter)(
		data_conv)
	return output_tensor_list

def conv_birelu_swap(nb_filter,filter_size,border_mode,input_shape,w_reg,gate_activation,index,layer_index,
                      input_tensor_list,relu_birelu_switch=1):
	tensor_concat =merge([input_tensor_list[0], input_tensor_list[1]], mode='concat', concat_axis=1,
	                     name='S_MergeInput_layer'+str(
		layer_index)+'_index-'+str(
		index))
	data_conv = Convolution2D(nb_filter, filter_size, filter_size, activation=None,
	                          input_shape=input_shape, border_mode=border_mode, W_regularizer=w_reg,
	                          name='S_conv_Swap_'+'nbfilter-'+str(nb_filter)+'_layer-'+str(layer_index)+'number'+str(
		                          index))(
		tensor_concat)
	output_tensor_list = Birelu(gate_activation,relu_birelu_sel=relu_birelu_switch,name='S_BiRelu_layer-'+str(
		layer_index)+'_index'+str(index))(
		data_conv)
	return output_tensor_list
def conv_relu_merge(nb_filter,filter_size,border_mode,input_shape,w_reg,gate_activation,index,layer_index,
                      input_tensor_list):
	tensor_concat = merge([input_tensor_list[0], input_tensor_list[1]], mode='concat', concat_axis=1,
	                      name='RM_concat_Merge_layer=' + str(layer_index) +'index-'+ str(index))


	data_conv = Convolution2D(nb_filter, filter_size, filter_size, activation=None, input_shape=input_shape,
	                          border_mode=border_mode, W_regularizer=w_reg,
	                          name='RM_conv_'+'nbfilter'+str(nb_filter) +'_layer-'+str(layer_index) + '_index' +
	                               str(
		index))(tensor_concat)
	output_tensor = Relu(gate_activation,name='RM_RELU_layer-'+str(layer_index)+'_index'+str(index))(data_conv)
	return output_tensor
def conv_birelu_merge(nb_filter,filter_size,border_mode,input_shape,w_reg,gate_activation,index,layer_index,
                      input_tensor_list):
	tensor_concat = merge([input_tensor_list[0], input_tensor_list[1]], mode='concat', concat_axis=1,
	                      name='BM_Merge_input_layer=' + str(layer_index) +'index-'+ str(index))


	data_conv = Convolution2D(nb_filter, filter_size, filter_size, activation=None, input_shape=input_shape,
	                          border_mode=border_mode, W_regularizer=w_reg,
	                          name='BM_conv_Merge_'+'nbfilter'+str(nb_filter) +'_layer-'+str(layer_index) + '_index' +
	                               str(
		index))(tensor_concat)
	output_tensor = Birelu(gate_activation,name='BM_Birelu_layer-'+str(layer_index)+'_index'+str(index))(data_conv)
	output_tensor = merge([output_tensor[0], output_tensor[1]], mode='concat', concat_axis=1,
	                      name='BM_Merge_output_layer=' + str(layer_index) + 'index-' + str(index))
	return output_tensor
def conv_relu(nb_filter,filter_size,border_mode,input_shape,w_reg,gate_activation,index,layer_index,
                      input_tensor,stride = 1,breg=None):
	data_conv = Conv2D(nb_filter, (filter_size, filter_size), activation=None, input_shape=input_shape,
	                          padding=border_mode, kernel_regularizer=w_reg,kernel_initializer='he_normal',
	                          name='CONV_L'+str(layer_index) + '_I' +
	                               str(index),b_regularizer=breg)(input_tensor)
	output_tensor = Relu(gate_activation,name='RELU_layer-'+str(layer_index)+'_index'+str(index))(data_conv)
	return output_tensor
def conv(nb_filter,filter_size,border_mode,input_shape,w_reg,gate_activation,index,layer_index,
                      input_tensor,stride = 1,breg=None):
	# data_conv = Convolution2D(nb_filter, filter_size, filter_size, activation=None, input_shape=input_shape,
	#                           border_mode=border_mode, W_regularizer=w_reg,
	#                           name='CONV_'+'nbfilter'+str(nb_filter) +'_layer-'+str(layer_index) + '_index' +
	#                                str(
	# 	index),subsample=(stride,stride),b_regularizer=breg,init='glorot_normal')(input_tensor)
	filter_size = int(filter_size)
	name = 'CONV_' + 'nbfilter' + str(nb_filter) + '_layer-' + str(
		                          layer_index) + '_index' + str(index)
	data_conv = Conv2D(nb_filter,(filter_size,filter_size), activation=None, input_shape=input_shape,
	                          border_mode=border_mode, W_regularizer=w_reg,
	                          name=name, subsample=(stride, stride), b_regularizer=breg,
	                          init='he_normal')(input_tensor)
	return data_conv
def concat(input_tensor_list,index,layer_index):
	tensor_concat = merge([input_tensor_list[0], input_tensor_list[1]], mode='concat', concat_axis=1,
	                      name='Merge_' + str(layer_index) + 'index-' + str(index))
	return tensor_concat