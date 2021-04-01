import argparse


def main():
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Detects keypoint locations in a 3d model.')
    parser.add_argument("input", help="Input mesh.")
    parser.add_argument("--method", default="mp-pose", choices=["mp-pose", "mp-face"],
                        help="Detection method.")

    args = parser.parse_args()

    main()
