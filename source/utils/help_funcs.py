import random, os
import numpy as np
import torch

def seed_everything(seed: int):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = True

def collate_fn(original_batch):
    batch = {}
    for k in original_batch[0].keys():
        batch[k] = [d[k] for d in original_batch]
    return batch

def listize_fn(original_batch):
    batch = {}
    for k in original_batch.keys():
        batch[k] = [original_batch[k]]
    return batch

def _save_checkpoint(model, optimizer, cur_epoch, args, is_best=False):
    """
    Save the checkpoint at the current epoch.
    """
    os.makedirs(f'{args.output_dir}/{args.split}/{args.data}', exist_ok=True)

    param_grad_dic = {
        name: param.requires_grad for (name, param) in model.named_parameters()
    }
    state_dict = model.state_dict()
    for k in list(state_dict.keys()):
        if k in param_grad_dic.keys() and not param_grad_dic[k]:
            # delete parameters that do not require gradient
            del state_dict[k]
    save_obj = {
        "model": state_dict,
        "optimizer": optimizer.state_dict(),
        "config": args,
        "epoch": cur_epoch,
    }
    path = f'{args.output_dir}/{args.split}/{args.data}/{args.model_name}_{args.llm_model_name}_llm_frozen{args.llm_frozen}_{args.num_epochs}epochs_lr{args.lr}_{args.split}_{"best" if is_best else cur_epoch}_{args.run_name}.pth'
    print("Saving checkpoint at epoch {} to {}".format(cur_epoch, path))
    torch.save(save_obj, path)

def _reload_model(model, checkpoint_path, strict=False):
    """
    Load the best checkpoint for evaluation.
    """
    print("Loading checkpoint from {}.".format(checkpoint_path))

    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    model.load_state_dict(checkpoint["model"], strict=strict)

    return model