from prompt_toolkit.shortcuts import radiolist_dialog

result = radiolist_dialog(
    title="RadioList dialog",
    text="Which breakfast would you like ?",
    values=[
        ("breakfast1", "Eggs and beacon"),
        ("breakfast2", "French breakfast"),
        ("breakfast3", "Equestrian breakfast")
    ]
).run()