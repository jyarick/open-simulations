# helpers/guards.py

import IPython.display as ipd

def require_users(state, n_min=1, where="this section", quiet=False, rich=True):
    ok = len(getattr(state, "modified_data", {})) >= int(n_min)
    if ok:
        return True

    if quiet:
        return False

    msg = f"⚠️ Add power users first to use {where}."
    if rich:
        ipd.display(ipd.HTML(
            f"<div style='border:1px solid #ddd; padding:10px; border-radius:10px; color:#555;'>"
            f"<b>{msg}</b>"
            f"</div>"
        ))
    else:
        print(msg)
    return False
