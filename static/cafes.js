"use strict";

const $likeButton = $("#like-btn");

/* Handles cafe like */
async function handleLikeBtnClick(evt) {
  let $cafeId = $(evt.target).parent();
  let cafeId = parseInt($cafeId.attr('cafe-data-id'));
  let userId = $cafeId.attr('logged-user');
  let btnStatus;

  let is_cafe_liked = await isLiked(userId, cafeId);

  if (is_cafe_liked.likes === false) {
    btnStatus = await likeCafe(userId, cafeId);
  } else {
    btnStatus = await unlikeCafe(userId, cafeId);
  }

  toogleLikeBtn(btnStatus);
}

/* Figures out if the current user likes a cafe */
async function isLiked(userId, cafeId) {
  const params = new URLSearchParams(
    {
      cafeId: cafeId,
      userId: userId
    }
  );

  const response = await fetch(`/api/likes?${params}`);
  const data = await response.json();

  return data;
}

/* Likes a cafe  */
async function likeCafe(userId, cafeId) {
  const response = await fetch(`/api/like`, {
    method: "POST",
    body: JSON.stringify({
      userId: userId,
      cafeId: cafeId
    }),
    headers: {
      "Content-Type": "application/json"
    }
  });

  const data = await response.json();

  return data;
}

/* Unlikes a cafe  */
async function unlikeCafe(userId, cafeId) {

  const response = await fetch(`/api/unlike`, {
    method: "POST",
    body: JSON.stringify({
      userId: userId,
      cafeId: cafeId
    }),
    headers: {
      "Content-Type": "application/json"
    }
  });

  const data = await response.json();

  return data;
}

/* Toogles button between liked and unliked */
function toogleLikeBtn(liked) {
  if (liked['unliked'] === undefined) {
    $likeButton.text("Liked");
  } else {
    $likeButton.text("Like");
  }
}

$likeButton.on("click", handleLikeBtnClick);