import traceback

import keras
from keras import optimizers
from modeldatabase.Binary_models import model_constructor_utils
from modeldatabase.Binary_models.model_db import get_model_from_db
from utils.gen_utils import *
from utils.modelutils import model_modification_utils
from utils.opt_utils import *
from utils.trainingutils.training_phases_utils import *


def check_model_list(model_list, datasets):
	opts = default_opt_creator()
	for dataset_str in datasets:
		for model in model_list:
			set_dataset(opts, dataset=dataset_str)
			set_default_opts_based_on_model_dataset(opts)
			set_model_string(opts, model)
			model_dict= get_model_from_db(model, opts)
			model = model_dict['model']
			model.summary()



if __name__ == '__main__':
	# gatenet_binary_merged_model lenet_amir ,gatenet_binary_model
	for total_params in [.5,3.7,1,2]:
	# total_params=1;
		models = ['vgg_baseline']
		datasets = ['cifar100','cifar10']
		experiment_name = get_experiment_name_prompt()
		check_model_list(models, datasets)
		print((keras.__version__))
		for dataset_str in datasets:
			# set dataset_params
			for model_str in models:
				try:

					print(100 * '*', 3 * '\n', model_str, '\n', dataset_str, 3 * '\n', 100 * '*')
					opts = default_opt_creator()
					opts['experiment_name'] = experiment_name

					set_dataset(opts, dataset=dataset_str)
					opts = set_model_string(opts, model_str)
					opts = set_default_opts_based_on_model_dataset(opts)

					input_shape = opts['training_opts']['dataset']['input_shape']
					nb_class = opts['training_opts']['dataset']['nb_classes']
					# opts = set_expand_rate(opts, param_expand_sel)
					# optimizer = optimizers.Nadam()
					optimizer = optimizers.SGD(lr=opts['optimizer_opts']['lr'], momentum=opts['optimizer_opts']['momentum'],
					                           decay=opts['optimizer_opts']['decay'], nesterov=opts['optimizer_opts']['nestrov'])
					# optimizer = optimizers.Adadelta()
					""" MODEL PREPARE """
					model_dict = get_model_from_db(model_str, opts)
					model = model_dict['model']
					model_total_params = (model.count_params() // 100000) / 10
					if (not total_params == 0) and (not model_total_params== total_params):
						set_expand_rate(opts, np.sqrt(total_params/model_total_params)*get_expand_rate(opts));
						print('Expand Rate Changed')
						model_dict = get_model_from_db(model_str, opts)
						model = model_dict['model']
					if total_params==0: total_params = model_total_params;

					opts['experiment_tag'] = experiment_name + '/' + dataset_str + '/' + model_str + '/' + str((model.count_params()//100000)/10)+'M'
					# out_tensor_list  = model_dict['out']
					# output_num  = len(out_tensor_list)
					model.summary()
					# model_modification_utils.load_weights_by_block_index_list(model, [1, 2, 3, 4, 5, 6, 7, 8, 9], os.path.join(
					# 	global_constant_var.get_experimentcase_abs_path(experiment_name, dataset_str, 'nin_tree_berp_1'), 'checkpoint'),
					#                                                           model_constructor_utils.CONVSH_NAME)
					model.compile(loss=opt_utils.get_loss(opts), optimizer=optimizer, metrics=opt_utils.get_metrics(opts))
					method_names = find_key_value_to_str_recursive(opts, '', {'param_expand'})
					opts['experiment_name'] = method_names
					# LOAD DATA
					(data_train, label_train), (data_test, label_test) = load_data(dataset_str, opts)
					data_train, data_test = preprocess_data_phase(opts, data_train, data_test)
					data_gen = data_augmentation_phase(opts)
					# COLLECT CALLBACKS
					callback_list = collect_callbacks(opts)

					# TRAIN
					samples_per_epoch = data_train.shape[0] if opts['training_opts']['samples_per_epoch'] == -1 else opts['training_opts'][
						'samples_per_epoch']
					model.fit_generator(
						data_gen.flow(data_train, label_train, batch_size=opts['training_opts']['batch_size'], shuffle=True, seed=opts['seed']),
						samples_per_epoch=samples_per_epoch, nb_epoch=opts['training_opts']['epoch_nb'], callbacks=callback_list,
						validation_data=(data_test, label_test))
				except:
					print(model_str, dataset_str)
					traceback.print_exc()
