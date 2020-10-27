from aircraft import Plan


def main():
    rules = {
        collecting_network_stats: {}
    }

    plan = Plan(name="Network Diagnostics",
                api_version="v1beta1",
                start_at=collecting_network_stats,
                rules=rules)
    plan.execute()


def collecting_network_stats(data):
    sudo(['ip', 'address'])
    return "collected", data


if __name__ == "__main__":
    main()
