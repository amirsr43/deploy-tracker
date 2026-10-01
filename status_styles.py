STATUS_STYLES = {
    "Success": {
        "background": ("#DCFCE7", "#14532D"),
        "text": ("#166534", "#BBF7D0")
    },
    "Failed": {
        "background": ("#FEE2E2", "#7F1D1D"),
        "text": ("#991B1B", "#FECACA")
    },
    "Pending": {
        "background": ("#FEF3C7", "#78350F"),
        "text": ("#92400E", "#FDE68A")
    },
    "Building": {
        "background": ("#DBEAFE", "#1E3A8A"),
        "text": ("#1E40AF", "#BFDBFE")
    },
    "Deploying": {
        "background": ("#EDE9FE", "#4C1D95"),
        "text": ("#5B21B6", "#DDD6FE")
    },
    "Rolled Back": {
        "background": ("#E5E7EB", "#374151"),
        "text": ("#374151", "#E5E7EB")
    }
}


def get_status_style(status):
    return STATUS_STYLES.get(
        status,
        {
            "background": ("#E5E7EB", "#4B5563"),
            "text": ("#374151", "#F9FAFB")
        }
    )
