import argparse
import fasttext


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_file", type=str, default="data/train_set/quality_train.txt")
    parser.add_argument("--valid_file", type=str, default="data/train_set/quality_valid.txt")
    parser.add_argument("--model_out", type=str, default="data/quality_classifier.bin")
    parser.add_argument("--lr", type=float, default=0.5)
    parser.add_argument("--epoch", type=int, default=20)
    parser.add_argument("--dim", type=int, default=100)
    parser.add_argument("--wordNgrams", type=int, default=2)
    args = parser.parse_args()

    model = fasttext.train_supervised(
        input=args.train_file,
        lr=args.lr,
        epoch=args.epoch,
        dim=args.dim,
        wordNgrams=args.wordNgrams,
        loss="softmax",
    )

    model.save_model(args.model_out)
    print(f"Saved model to {args.model_out}")

    result = model.test(args.valid_file)
    print("Validation result:", result)


if __name__ == "__main__":
    main()