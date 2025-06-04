document.addEventListener("DOMContentLoaded", function () {
  const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

  document.querySelectorAll('.like-button').forEach(button => {
    button.addEventListener('click', function () {
      const postId = this.dataset.postId;
      const likeCountElem = this.querySelector('.like-count');
      const isLiked = this.classList.contains('liked');

      fetch(`/like-post/${postId}`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})  // Empty for now
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          likeCountElem.textContent = data.likes;
          this.classList.toggle('liked', data.liked);

          this.title = data.liked
            ? "You already like this Post."
            : "Like this Post!";
        }
      });
    });
  });
});